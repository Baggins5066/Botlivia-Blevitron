import aiohttp
import json
from colorama import Fore
from config import LLM_API_KEY, PERSONA_TEXT, BAGGINS_ID, SNAZZYDADDY_ID
from utils import log

# -------- AI Decision: Should Bot Reply? --------
async def should_bot_reply(message, history):
    # Build context from recent conversation
    history_text = "\n".join([f"{h['author']}: {h['content']}" for h in history[-5:]])

    decision_prompt = f"""You are deciding whether "Meat Bro" (a Discord bot) should respond to this message.

Recent conversation:
{history_text}

Current message from {message.author}: {message.content}

DEFAULT TO NO. Only respond YES if one of these conditions is clearly met:

RESPOND YES ONLY IF:
1. The message directly mentions "Meat Bro" or "meat bro" (bot name)
2. The message is clearly a direct reply or question to the bot
3. Someone explicitly asks the bot for advice/input (e.g., "what do you think?", "meat bro?")
4. The message tags or @mentions the bot

ALWAYS RESPOND NO IF:
- Two or more people are having a conversation with each other (even about fitness/gym topics)
- It's casual banter between users that doesn't need bot input
- The message is a statement or comment not directed at anyone specific
- Simple acknowledgments like "ok", "lol", "nice", "yeah", "cool"
- The bot responded in the last 2 messages (unless directly mentioned/asked)
- People are just sharing updates or stories with each other

When in doubt, answer NO. The bot should NOT interrupt conversations.

Answer: """

    payload = {
        "contents": [{"parts": [{"text": decision_prompt}]}],
        "systemInstruction": {"parts": [{"text": "You are a decision-making assistant. Respond with only YES or NO."}]}
    }

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key={LLM_API_KEY}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers={"Content-Type": "application/json"}, data=json.dumps(payload)) as resp:
                response_data = await resp.json()
                if response_data and response_data.get("candidates"):
                    decision = response_data["candidates"][0]["content"]["parts"][0]["text"].strip().upper()
                    log(f"[AI DECISION] Should reply: {decision}", Fore.YELLOW)
                    return "YES" in decision
    except Exception as e:
        log(f"[AI DECISION ERROR] {e}, defaulting to NO", Fore.RED)

    return False

# -------- LLM Response --------
async def get_llm_response(prompt, current_user_id=None):
    persona = PERSONA_TEXT
    if current_user_id == BAGGINS_ID:
        persona += "\n\nIMPORTANT: You are currently talking to Baggins directly. Do NOT mention or tag Baggins in your response. Refer to him as boss, bossman, boss dawg, or something adjacent."
    elif current_user_id == SNAZZYDADDY_ID:
        persona += "\n\nIMPORTANT: You are currently talking to Snazzy Daddy directly. Do NOT mention or tag Snazzy Daddy in your response. Refer to him as boss, bossman, boss dawg, or something adjacent."

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "systemInstruction": {"parts": [{"text": persona}]}
    }

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key={LLM_API_KEY}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers={"Content-Type": "application/json"}, data=json.dumps(payload)) as resp:
                response_data = await resp.json()
                if response_data and response_data.get("candidates"):
                    return response_data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        log(f"[LLM ERROR] {e}", Fore.RED)

    return "huh"


# -------- Status Generation --------
async def generate_statuses(example_statuses):
    log("[STATUS] Generating new statuses...", Fore.CYAN)

    examples_text = "\n- ".join(example_statuses)
    prompt = f"""Generate a list of 24 unique, short, casual, and satirically funny statuses for a Discord bot named "Meat Bro".

These statuses should be inspired by the following examples, but not identical:
- {examples_text}

The statuses should be in the same vibe and tone as the examples. Each status should be on a new line. Do not include any extra text or formatting.
"""

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "systemInstruction": {"parts": [{"text": "You are a creative assistant. Generate a list of 24 Discord statuses."}]}
    }

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key={LLM_API_KEY}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers={"Content-Type": "application/json"}, data=json.dumps(payload)) as resp:
                response_data = await resp.json()
                if response_data and response_data.get("candidates"):
                    text = response_data["candidates"][0]["content"]["parts"][0]["text"]
                    statuses = [status.strip() for status in text.split("\n") if status.strip()]
                    log(f"[STATUS] Generated {len(statuses)} new statuses.", Fore.GREEN)
                    return statuses
    except Exception as e:
        log(f"[STATUS GEN ERROR] {e}", Fore.RED)

    return []