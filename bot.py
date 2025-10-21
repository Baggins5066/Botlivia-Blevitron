import discord
import random
from discord.ext import tasks
from collections import deque
from colorama import Fore

import config
from utils import log, replace_with_mentions
from llm import should_bot_reply, get_llm_response, generate_statuses

# -------- Discord Bot Setup --------
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
client = discord.Client(intents=intents)

conversation_history = {}   # short memory per channel
processed_messages = deque(maxlen=1000)  # track processed message IDs to prevent duplicates
generated_statuses = deque()

# -------- Discord Events --------
@client.event
async def on_ready():
    if client.user:
        log(f"[READY] Logged in as {client.user} (ID: {client.user.id})", Fore.GREEN)
    cycle_presence.start()

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # Prevent processing the same message twice
    if message.id in processed_messages:
        return
    processed_messages.append(message.id)

    log(f"[INCOMING][#{message.channel}] {message.author}: {message.content}", Fore.CYAN)

    perms = message.channel.permissions_for(message.guild.me)
    if not (perms.send_messages and perms.read_messages):
        return

    history = conversation_history.get(message.channel.id, [])
    history.append({"author": str(message.author), "content": message.content})
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
            prompt = (
                f"Recent chat history:\n{history}\n\n"
                f"User: {message.content}"
            )
            response = await get_llm_response(prompt, current_user_id=message.author.id)
            response = replace_with_mentions(response)
            log(f"[OUTGOING][#{message.channel}] {client.user}: {response}", Fore.GREEN)
            await message.channel.send(response)

            # Add bot's response to history
            history.append({"author": str(client.user), "content": response})
            conversation_history[message.channel.id] = history

@tasks.loop(hours=1)
async def cycle_presence():
    global generated_statuses
    if not generated_statuses:
        new_statuses = await generate_statuses(config.ALL_STATUSES)
        if new_statuses:
            generated_statuses.extend(new_statuses)

    if generated_statuses:
        status = generated_statuses.popleft()
    else:
        status = random.choice(config.ALL_STATUSES)

    log(f"[STATUS] Blevitron is now: {status}", Fore.YELLOW)
    await client.change_presence(activity=discord.CustomActivity(name=status))

# -------- Run Bot --------
if __name__ == "__main__":
    if not config.DISCORD_BOT_TOKEN:
        log("[ERROR] DISCORD_BOT_TOKEN environment variable is not set!", Fore.RED)
        exit(1)
    if not config.LLM_API_KEY:
        log("[ERROR] LLM_API_KEY environment variable is not set!", Fore.RED)
        exit(1)

    client.run(config.DISCORD_BOT_TOKEN)