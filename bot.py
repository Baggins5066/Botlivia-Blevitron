import discord
import random
from discord.ext import tasks
from colorama import Fore

import config
from utils import log

# -------- Discord Bot Setup --------
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# -------- Discord Events --------
@client.event
async def on_ready():
    if client.user:
        log(f"[READY] Logged in as {client.user} (ID: {client.user.id})", Fore.GREEN)
    cycle_presence.start()

@client.event
async def on_message(message):
    # Don't respond to ourselves
    if message.author == client.user:
        return

    log(f"[INCOMING][#{message.channel}] {message.author}: {message.content}", Fore.CYAN)

    # Handle DMs (where guild is None)
    if message.guild is None:
        if client.user in message.mentions:
            response = f"Hello! I'm {config.BOT_NAME}, a Discord bot!"
            log(f"[OUTGOING][DM] {client.user}: {response}", Fore.GREEN)
            await message.channel.send(response)
        return

    # Check permissions in guild channels
    perms = message.channel.permissions_for(message.guild.me)
    if not (perms.send_messages and perms.read_messages):
        return

    # Respond when mentioned
    if client.user in message.mentions:
        if perms.send_messages:
            response = f"Hello! I'm {config.BOT_NAME}, a Discord bot!"
            log(f"[OUTGOING][#{message.channel}] {client.user}: {response}", Fore.GREEN)
            await message.channel.send(response)

@tasks.loop(hours=1)
async def cycle_presence():
    status = random.choice(config.ALL_STATUSES)
    log(f"[STATUS] {config.BOT_NAME} is now: {status}", Fore.YELLOW)
    await client.change_presence(activity=discord.Game(name=status))

# -------- Run Bot --------
if __name__ == "__main__":
    if not config.DISCORD_BOT_TOKEN:
        log("[ERROR] DISCORD_BOT_TOKEN environment variable is not set!", Fore.RED)
        exit(1)

    client.run(config.DISCORD_BOT_TOKEN)
