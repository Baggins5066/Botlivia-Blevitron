import aiohttp
import asyncio
import json
from colorama import Fore
from config import LLM_API_KEY
from utils import log
from memory_search import get_relevant_memories
from user_management import replace_aliases_with_usernames

# -------- AI Decision: Should Bot Reply? --------
async def should_bot_reply(message, history):
    # Process aliases in the message content and history
    processed_content = replace_aliases_with_usernames(message.content)
    processed_history = [
        {"author": h['author'], "content": replace_aliases_with_usernames(h['content'])}
        for h in history
    ]

    # Build context from recent conversation
    history_text = "\n".join([f"{h['author']}: {h['content']}" for h in processed_history[-10:]])

    # Get relevant memories from the database
    memories = await get_relevant_memories(processed_content, processed_history, limit=40)
    memory_text = "\n".join([f"- {mem}" for mem in memories])

    decision_prompt = f"""You are deciding whether "Botlivia Blevitron" (a Discord bot) should respond to this message.

Recent conversation:
{history_text}

Here are some relevant past messages from the database for context:
{memory_text}

Current message from {message.author}: {message.content}

Should the bot respond to this message?
Return only YES or NO.

Current message from {message.author}: {message.content}
Answer: """

    payload = {
        "contents": [{"parts": [{"text": decision_prompt}]}],
        "systemInstruction": {"parts": [{"text": "You are a decision-making assistant. Respond with only YES or NO."}]}
    }

    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent"
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": LLM_API_KEY
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=json.dumps(payload)) as resp:
                response_data = await resp.json()
                if response_data and response_data.get("candidates"):
                    decision = response_data["candidates"][0]["content"]["parts"][0]["text"].strip().upper()
                    log(f"[AI DECISION] Should reply: {decision}", Fore.YELLOW)
                    return "YES" in decision
    except Exception as e:
        log(f"[AI DECISION ERROR] {e}, defaulting to NO", Fore.RED)

    return False

# -------- LLM Response --------
async def get_llm_response(prompt, history=None, user_id=None):
    # Process aliases in the prompt and history
    processed_prompt = replace_aliases_with_usernames(prompt)
    processed_history = [
        {"author": h['author'], "content": replace_aliases_with_usernames(h['content'])}
        for h in (history or [])
    ]

    # Load user data from JSON file
    try:
        with open('users.json', 'r') as f:
            user_data = json.load(f)
    except FileNotFoundError:
        user_data = {}

    # Retrieve relevant memories from past conversations
    try:
        current_message = processed_prompt.split("User: ")[-1] if "User: " in processed_prompt else processed_prompt
        memories = await get_relevant_memories(current_message, processed_history, limit=40)
        
        if memories:
            memory_text = "\n".join([f"- {mem}" for mem in memories])
            processed_prompt = f"[Relevant past messages for context]:\n{memory_text}\n\n{processed_prompt}"
            log(f"[MEMORY] Retrieved {len(memories)} relevant memories", Fore.MAGENTA)
    except Exception as e:
        log(f"[MEMORY ERROR] {e}, continuing without memories", Fore.YELLOW)

    # Base system instruction
    system_instruction = "You are Blevitron. Talk like the messages you see in the chat history."

    # Add user-specific instructions if user_id is provided
    if user_id and str(user_id) in user_data:
        user_info = user_data[str(user_id)]
        system_instruction += f"\n\nThis is how you should act towards {user_info['username']}:\n{user_info['description']}"

    payload = {
        "contents": [{"parts": [{"text": processed_prompt}]}],
        "systemInstruction": {
            "parts": [{"text": system_instruction}]
        }
    }

    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent"
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": LLM_API_KEY
    }

    # Retry logic with exponential backoff
    max_retries = 3
    base_delay = 1
    
    for attempt in range(max_retries):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, data=json.dumps(payload)) as resp:
                    if resp.status == 503:
                        if attempt < max_retries - 1:
                            delay = base_delay * (2 ** attempt)
                            log(f"[LLM RETRY] API overloaded, retrying in {delay}s (attempt {attempt + 1}/{max_retries})", Fore.YELLOW)
                            await asyncio.sleep(delay)
                            continue
                        else:
                            log(f"[LLM ERROR] API still overloaded after {max_retries} attempts", Fore.RED)
                            return "sorry, i'm having trouble connecting to my brain rn. try again in a sec?"
                    
                    if resp.status != 200:
                        error_text = await resp.text()
                        log(f"[LLM ERROR] API returned status {resp.status}: {error_text}", Fore.RED)
                        return "uh idk"
                    
                    response_data = await resp.json()
                    log(f"[LLM RESPONSE] Raw response: {json.dumps(response_data)[:200]}", Fore.CYAN)
                    
                    if response_data and response_data.get("candidates"):
                        return response_data["candidates"][0]["content"]["parts"][0]["text"]
                    else:
                        log(f"[LLM ERROR] No candidates in response: {response_data}", Fore.RED)
                        return "uh idk"
        except Exception as e:
            log(f"[LLM ERROR] Exception occurred: {type(e).__name__}: {e}", Fore.RED)
            import traceback
            log(f"[LLM ERROR] Traceback: {traceback.format_exc()}", Fore.RED)
            
            if attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt)
                log(f"[LLM RETRY] Retrying in {delay}s (attempt {attempt + 1}/{max_retries})", Fore.YELLOW)
                await asyncio.sleep(delay)
                continue

    return "uh idk"