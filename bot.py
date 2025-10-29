import discord
from discord.ext import commands
from collections import deque
from colorama import Fore
from flask import Flask, send_file
from threading import Thread

import config
from utils import log, replace_with_mentions
from llm import should_bot_reply, get_llm_response

# -------- Flask Web Server for Log Access --------
app = Flask(__name__)

@app.route('/')
def index():
    return '<h1>Bot is running!</h1><a href="/logs">View Logs</a>'

@app.route('/logs')
def view_logs():
    try:
        return send_file('bot.log', mimetype='text/plain')
    except FileNotFoundError:
        return 'Log file not found', 404

def run_flask():
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

# -------- Discord Bot Setup --------
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

conversation_history = {}   # short memory per channel
processed_messages = deque(maxlen=1000)  # track processed message IDs to prevent duplicates

# -------- Discord Events --------
@bot.event
async def on_ready():
    if bot.user:
        log(f"[READY] Logged in as {bot.user} (ID: {bot.user.id})", Fore.GREEN)
        try:
            await bot.load_extension("commands")
            synced = await bot.tree.sync()
            log(f"Synced {len(synced)} command(s)", Fore.GREEN)
        except Exception as e:
            log(f"Failed to sync commands: {e}", Fore.RED)

@bot.event
async def on_message(message):
    sleep_cog = bot.get_cog("SleepCog")
    if sleep_cog and sleep_cog.is_sleeping:
        return

    try:
        if message.author == bot.user:
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

        history = conversation_history.get(message.channel.id, [])
        history.append({"author": str(message.author), "content": message.content})
        if len(history) > 10:
            history = history[-10:]
        conversation_history[message.channel.id] = history

        # Check if message is a direct reply to bot or mentions bot
        is_direct_reply = message.reference and message.reference.resolved and message.reference.resolved.author == bot.user
        is_bot_mentioned = bot.user in message.mentions or "botlivia blevitron" in message.content.lower()

        # Auto-reply if directly mentioned or replied to
        if is_direct_reply or is_bot_mentioned:
            should_reply = True
        else:
            # Use AI to decide if bot should reply
            try:
                should_reply = await should_bot_reply(message, history)
            except Exception as e:
                log(f"[ERROR] Failed to determine if bot should reply: {e}", Fore.RED)
                should_reply = False

        if should_reply and perms.send_messages:
            async with message.channel.typing():
                try:
                    prompt = (
                        f"Recent chat history:\n{history}\n\n"
                        f"User: {message.content}"
                    )
                    response = await get_llm_response(prompt, history=history, user_id=message.author.id)
                    response = replace_with_mentions(response)
                    log(f"[OUTGOING][#{message.channel}] {bot.user}: {response}", Fore.GREEN)
                    await message.channel.send(response)

                    # Add bot's response to history
                    history.append({"author": str(bot.user), "content": response})
                    conversation_history[message.channel.id] = history
                except Exception as e:
                    log(f"[ERROR] Failed to generate or send response: {e}", Fore.RED)
    except Exception as e:
        log(f"[ERROR] Unexpected error in on_message: {e}", Fore.RED)

# -------- Run Bot --------
if __name__ == "__main__":
    if not config.DISCORD_BOT_TOKEN:
        log("[ERROR] DISCORD_BOT_TOKEN environment variable is not set!", Fore.RED)
        exit(1)
    if not config.LLM_API_KEY:
        log("[ERROR] LLM_API_KEY environment variable is not set!", Fore.RED)
        exit(1)

    # Start Flask server in background thread
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()
    log("[FLASK] Web server started on port 5000", Fore.GREEN)

    bot.run(config.DISCORD_BOT_TOKEN)