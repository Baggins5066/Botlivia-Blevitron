import aiohttp
import json
from colorama import Fore
from config import LLM_API_KEY, BAGGINS_ID, SNAZZYDADDY_ID, PHROGSLEG_ID, CORN_ID, PUGMONKEY_ID, MEATBRO_ID, RESTORT_ID, TBL_ID, EVAN_ID, DROID_ID
from utils import log
from memory_search import get_relevant_memories

# -------- AI Decision: Should Bot Reply? --------
async def should_bot_reply(message, history):
    # Build context from recent conversation
    history_text = "\n".join([f"{h['author']}: {h['content']}" for h in history[-10:]])

    # Get relevant memories from the database
    memories = await get_relevant_memories(message.content, history, limit=40)
    memory_text = "\n".join([f"- {mem}" for mem in memories])

    decision_prompt = f"""You are deciding whether "Botlivia Blevitron" (a Discord bot) should respond to this message.

Recent conversation:
{history_text}

Here are some relevant past messages from the database for context:
{memory_text}

Current message from {message.author}: {message.content}

Respond with ONLY "YES" or "NO".
- Consider if the message is directed at the bot, mentions the bot, or is a question/statement the bot should engage with.
- Based on the provided memories, is this a topic the bot would typically respond to?
- Is this a casual chat between other users that doesn't need bot input?
- Has the bot responded recently? Avoid spamming.

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
async def get_llm_response(prompt, history=None):
    # Retrieve relevant memories from past conversations
    try:
        current_message = prompt.split("User: ")[-1] if "User: " in prompt else prompt
        memories = await get_relevant_memories(current_message, history or [], limit=40)
        
        if memories:
            memory_text = "\n".join([f"- {mem}" for mem in memories])
            prompt = f"[Relevant past messages for context]:\n{memory_text}\n\n{prompt}"
            log(f"[MEMORY] Retrieved {len(memories)} relevant memories", Fore.MAGENTA)
    except Exception as e:
        log(f"[MEMORY ERROR] {e}, continuing without memories", Fore.YELLOW)
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "systemInstruction": {
            "parts": [{
                "text": """
Talk like the messages you see in the chat history.
"""
            }]
        }
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