import discord
from collections import deque
from colorama import Fore
import asyncio

import config
from utils import log, replace_with_mentions
from llm import should_bot_reply, get_llm_response
from user_profiles_local import (
    get_user_profile, 
    set_user_description, 
    get_all_profiles
)
from message_storage import store_message_async, clean_message_content

# -------- Discord Bot Setup --------
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
client = discord.Client(intents=intents)

conversation_history = {}   # short memory per channel
processed_messages = deque(maxlen=1000)  # track processed message IDs to prevent duplicates

# -------- Command Handlers --------
async def handle_commands(message):
    """Handle bot commands for profile management"""
    content = message.content.strip()
    
    # !profile [user] - View user profile
    if content.startswith('!profile'):
        parts = content.split(maxsplit=1)
        if len(parts) == 1:
            # Show own profile
            target_user = message.author
        else:
            # Show mentioned user's profile
            if message.mentions:
                target_user = message.mentions[0]
            else:
                await message.channel.send("❌ Please mention a user to view their profile.")
                return
        
        profile = get_user_profile(target_user.id)
        if profile and profile.get('description', '').strip():
            description = profile['description']
            response = f"**Profile for {target_user.display_name}:**\n{description}"
        else:
            response = f"No profile found for {target_user.display_name}."
        
        await message.channel.send(response)
        log(f"[COMMAND] !profile for {target_user.display_name}", Fore.CYAN)
    
    # !setdesc [user] [description] - Set description for user profile
    elif content.startswith('!setdesc'):
        parts = content.split(maxsplit=2)
        if len(parts) < 3 or not message.mentions:
            await message.channel.send("❌ Usage: `!setdesc @user [description text]`")
            return
        
        target_user = message.mentions[0]
        description_text = parts[2]
        
        try:
            success = set_user_description(target_user.id, target_user.display_name, description_text)
            if success:
                await message.channel.send(f"✅ Updated description for {target_user.display_name}'s profile.")
                log(f"[COMMAND] !setdesc for {target_user.display_name}", Fore.CYAN)
        except ValueError as e:
            await message.channel.send(f"❌ {str(e)}")
        except Exception as e:
            log(f"[ERROR] !setdesc failed: {e}", Fore.RED)
            await message.channel.send("❌ Failed to update description.")
    
    # !profiles - List all profiles
    elif content.startswith('!profiles'):
        try:
            profiles = get_all_profiles()
            if profiles:
                profile_list = []
                for p in profiles:
                    desc = p.get('description', '')
                    preview = (desc[:50] + '...') if len(desc) > 50 else desc
                    if preview:
                        profile_list.append(f"• **{p['username']}**: {preview}")
                    else:
                        profile_list.append(f"• **{p['username']}**: (no description)")
                response = "**All User Profiles:**\n" + "\n".join(profile_list)
            else:
                response = "No user profiles found."
            
            await message.channel.send(response)
            log(f"[COMMAND] !profiles - {len(profiles)} profiles", Fore.CYAN)
        except Exception as e:
            log(f"[ERROR] !profiles failed: {e}", Fore.RED)
            await message.channel.send("❌ Failed to retrieve profiles.")
    
    # !help - Show command help
    elif content.startswith('!help'):
        help_text = """**User Profile Commands:**
• `!profile [@user]` - View user profile (defaults to your own)
• `!setdesc @user [text]` - Set contextual information about your relationship with a user
• `!profiles` - List all user profiles
• `!help` - Show this help message

**Example:**
`!setdesc @Baggins This is Aiden, your ex-boyfriend from a few years ago. You still have feelings for him.`

**Note:** User profiles provide factual context about relationships and background. The bot learns its personality and speaking style from past conversation history in the database. Descriptions are visible to anyone who can use commands."""
        await message.channel.send(help_text)
        log(f"[COMMAND] !help", Fore.CYAN)

# -------- Discord Events --------
@client.event
async def on_ready():
    if client.user:
        log(f"[READY] Logged in as {client.user} (ID: {client.user.id})", Fore.GREEN)

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # Prevent processing the same message twice
    if message.id in processed_messages:
        return
    processed_messages.append(message.id)

    log(f"[INCOMING][#{message.channel}] {message.author}: {message.content}", Fore.CYAN)

    # Handle DM channels (no guild)
    if not message.guild:
        log(f"[DM] Ignoring DM from {message.author}", Fore.YELLOW)
        return

    perms = message.channel.permissions_for(message.guild.me)
    if not (perms.send_messages and perms.read_messages):
        return

    # Handle profile management commands
    if message.content.startswith('!'):
        await handle_commands(message)
        return

    # Store user message in ChromaDB with clean username and Discord message ID
    username = message.author.display_name or message.author.name
    asyncio.create_task(store_message_async(username, message.content, message.id))

    # Clean message content for conversation history (remove user ID mentions)
    cleaned_content = clean_message_content(message.content)
    
    history = conversation_history.get(message.channel.id, [])
    history.append({"author": str(message.author), "content": cleaned_content})
    if len(history) > 10:
        history = history[-10:]
    conversation_history[message.channel.id] = history

    # Check if message is a direct reply to bot or mentions bot
    is_direct_reply = message.reference and message.reference.resolved and message.reference.resolved.author == client.user
    is_bot_mentioned = client.user in message.mentions or "botlivia blevitron" in message.content.lower()

    # Auto-reply if directly mentioned or replied to
    if is_direct_reply or is_bot_mentioned:
        should_reply = True
    else:
        # Use AI to decide if bot should reply
        should_reply = await should_bot_reply(message, history)

    if should_reply and perms.send_messages:
        async with message.channel.typing():
            # Clean the current message before sending to LLM
            current_message_cleaned = clean_message_content(message.content)
            prompt = (
                f"Recent chat history:\n{history}\n\n"
                f"User: {current_message_cleaned}"
            )
            response = await get_llm_response(prompt, current_user_id=message.author.id, history=history)
            response = replace_with_mentions(response)
            log(f"[OUTGOING][#{message.channel}] {client.user}: {response}", Fore.GREEN)
            await message.channel.send(response)

            # Store bot's response in ChromaDB (cleaned version)
            if client.user:
                bot_username = client.user.display_name or client.user.name
                asyncio.create_task(store_message_async(bot_username, response))

            # Add bot's response to history (also cleaned)
            cleaned_response = clean_message_content(response)
            history.append({"author": str(client.user), "content": cleaned_response})
            conversation_history[message.channel.id] = history

# -------- Run Bot --------
if __name__ == "__main__":
    if not config.DISCORD_BOT_TOKEN:
        log("[ERROR] DISCORD_BOT_TOKEN environment variable is not set!", Fore.RED)
        exit(1)
    if not config.LLM_API_KEY:
        log("[ERROR] LLM_API_KEY environment variable is not set!", Fore.RED)
        exit(1)

    client.run(config.DISCORD_BOT_TOKEN)
