import aiohttp
import json
from colorama import Fore
from config import LLM_API_KEY
from utils import log
from memory_search import get_relevant_memories
from user_profiles_local import format_profile_context

# -------- AI Decision: Should Bot Reply? --------
async def should_bot_reply(message, history):
    # Build context from recent conversation
    history_text = "\n".join([f"{h['author']}: {h['content']}" for h in history[-10:]])

    decision_prompt = f"""You are deciding whether a Discord bot should respond to this message.

Recent conversation:
{history_text}


Current message from {message.author}: {message.content}

Respond with ONLY "YES" or "NO" based on these rules:
- YES if the message is directed at the bot or mentions the bot
- YES if the conversation seems to expect or need a response from the bot
- YES if someone is asking a question or making a statement that warrants engagement
- NO if it's a casual chat between other users that doesn't need bot input
- NO if the message is very short/simple like "ok", "lol", "nice" (unless directly replying to the bot)
- NO if the bot just responded recently (within last 2 messages) unless directly addressed

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
async def get_llm_response(prompt, current_user_id=None, history=None):
    # Get user profile context for personalization
    user_context = ""
    if current_user_id:
        try:
            user_context = format_profile_context(current_user_id)
            if user_context:
                log(f"[PROFILE] Loaded profile for user {current_user_id}", Fore.CYAN)
        except Exception as e:
            log(f"[PROFILE ERROR] {e}, continuing without user profile", Fore.YELLOW)
    
    # Retrieve relevant memories from past conversations (all users treated equally)
    try:
        current_message = prompt.split("User: ")[-1] if "User: " in prompt else prompt
        memories = await get_relevant_memories(current_message, history or [], limit=40)
        
        if memories:
            memory_text = "\n".join(memories)
            # Use memories as the primary context for generating response
            context_parts = []
            
            if user_context:
                context_parts.append(user_context)
            
            context_parts.append(f"""[CONVERSATION HISTORY FROM DATABASE - Use these past messages to inform your response]:
{memory_text}""")
            
            full_context = "\n\n".join(context_parts)
            
            full_prompt = f"""{full_context}

[CURRENT CONVERSATION]:
{prompt}

{'IMPORTANT: Follow the user profile instructions exactly - it defines your complete personality, tone, and speaking style when talking to this person.' if user_context else ''} Use the conversation history above for factual context and topics only{', not for speaking style' if user_context else ' and to inform your response style'}."""
            log(f"[MEMORY] Retrieved {len(memories)} relevant messages from database", Fore.MAGENTA)
        else:
            if user_context:
                full_prompt = f"""{user_context}

[CURRENT CONVERSATION]:
{prompt}

Based on the user profile information above, formulate an appropriate personalized response."""
            else:
                full_prompt = prompt
            log(f"[MEMORY] No relevant memories found, using current context only", Fore.YELLOW)
    except Exception as e:
        log(f"[MEMORY ERROR] {e}, continuing without memories", Fore.YELLOW)
        full_prompt = prompt

    payload = {
        "contents": [{"parts": [{"text": full_prompt}]}],
        "systemInstruction": {"parts": [{"text": "You are Blevitron, a Discord bot. Each user has a unique profile that defines your complete personality and behavior when talking to them - how you speak, your tone, your attitude, and your relationship with that person. Follow the user profile instructions exactly. Use the conversation history from the database for factual context, topics, and reference, but the user profile controls your personality and speaking style for each person."}]}
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

    return "idk"

# -------- Generate Custom Statuses --------
async def generate_statuses(base_statuses):
    """Generate creative status messages using AI"""
    prompt = f"""Generate 5 creative, quirky Discord custom status messages for a bot named "Botlivia Blevitron". 
Make them fun, slightly absurd, and unique. They should be short (under 50 characters).

Base examples for inspiration: {', '.join(base_statuses[:3])}

Return ONLY the 5 statuses, one per line, no numbers or formatting."""

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "systemInstruction": {"parts": [{"text": "You are a creative assistant. Return only the requested content, no extra formatting."}]}
    }

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key={LLM_API_KEY}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers={"Content-Type": "application/json"}, data=json.dumps(payload)) as resp:
                response_data = await resp.json()
                if response_data and response_data.get("candidates"):
                    text = response_data["candidates"][0]["content"]["parts"][0]["text"]
                    
                    # Parse and sanitize statuses
                    import re
                    statuses = []
                    for line in text.split('\n'):
                        line = line.strip()
                        if not line:
                            continue
                        # Remove leading numbers, bullets, or dashes
                        line = re.sub(r'^[\d\-\*\•]+[\.\):\s]*', '', line)
                        line = line.strip()
                        # Enforce max length
                        if len(line) > 50:
                            line = line[:47] + "..."
                        # Avoid duplicates with base statuses
                        if line and line.lower() not in [s.lower() for s in base_statuses]:
                            statuses.append(line)
                    
                    # Cap to 5 statuses
                    statuses = statuses[:5]
                    log(f"[STATUSES] Generated {len(statuses)} new statuses", Fore.YELLOW)
                    return statuses if statuses else []
    except Exception as e:
        log(f"[STATUS GEN ERROR] {e}", Fore.RED)

    return []