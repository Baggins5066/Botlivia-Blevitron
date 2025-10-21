import aiohttp
import json
from colorama import Fore
from config import LLM_API_KEY, PERSONA_TEXT, BAGGINS_ID, SNAZZYDADDY_ID
from utils import log

# -------- AI Decision: Should Bot Reply? --------
async def should_bot_reply(message, history):
    # Build context from recent conversation
    history_text = "\n".join([f"{h['author']}: {h['content']}" for h in history[-5:]])

    decision_prompt = f"""You are deciding whether "Botlivia Blevitron" (a Discord bot) should respond to this message.

Recent conversation:
{history_text}

Current message from {message.author}: {message.content}
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

    return "uh idk"