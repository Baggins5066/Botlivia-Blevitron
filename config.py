import os

# -------- BOT CONFIG --------
DISCORD_BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
LLM_API_KEY = os.environ.get("LLM_API_KEY")

# User IDs for mentions
BAGGINS_ID = 280188106412523521
SNAZZYDADDY_ID = 581161136129310730

# Bot's persona
PERSONA_TEXT = """You are Botlivia Blevitron, a quirky and friendly Discord bot. You're witty, helpful, and occasionally a bit sarcastic. 
You like to keep conversations fun and engaging. You're knowledgeable but don't take yourself too seriously. 
Keep your responses conversational and relatively brief unless asked for detailed explanations."""

# Status messages for the bot
ALL_STATUSES = [
    "contemplating the void",
    "vibing with the pixels",
    "debugging the matrix",
    "lost in the sauce",
    "touching grass (digitally)",
    "pondering the orb",
    "chaos mode activated",
    "simply existing",
    "professionally confused"
]