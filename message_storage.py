"""
Message storage module for storing live Discord messages in ChromaDB.
Handles async embedding generation and storage without blocking the bot.
"""

import asyncio
import hashlib
import re
from colorama import Fore
from utils import log
from chromadb_storage import add_messages
from embedding_pipeline import generate_embedding


def clean_message_content(content):
    """
    Clean message content by removing or replacing Discord-specific formatting.
    
    Args:
        content: Raw message content
        
    Returns:
        Cleaned message content
    """
    # Remove Discord user ID mentions like <@123456789> or <@!123456789>
    # These will be meaningless in the future and clutter the database
    cleaned = re.sub(r'<@!?\d+>', '[user]', content)
    
    # Remove channel mentions like <#123456789>
    cleaned = re.sub(r'<#\d+>', '[channel]', cleaned)
    
    # Remove role mentions like <@&123456789>
    cleaned = re.sub(r'<@&\d+>', '[role]', cleaned)
    
    return cleaned


async def store_message_async(author, message_content, message_id=None):
    """
    Store a message in ChromaDB asynchronously.
    Generates embedding and stores without blocking the bot.
    
    Args:
        author: Username of the message author
        message_content: Content of the message
        message_id: Optional unique message ID (e.g., Discord message ID)
    """
    try:
        # Clean the message content (remove user ID mentions)
        cleaned_content = clean_message_content(message_content)
        
        # Generate embedding for the cleaned message
        embedding = await generate_embedding(cleaned_content)
        
        # Generate message ID - use provided ID or let ChromaDB generate one
        # This prevents deduplication of similar messages from different users
        if message_id is None:
            import time
            # Use timestamp + author + content snippet for uniqueness
            unique_str = f"{time.time()}_{author}_{cleaned_content[:50]}"
            message_id = hashlib.sha256(unique_str.encode('utf-8')).hexdigest()
        else:
            # Use provided message ID (e.g., Discord message ID)
            message_id = str(message_id)
        
        # Store in ChromaDB (run in executor to avoid blocking)
        loop = asyncio.get_event_loop()
        added = await loop.run_in_executor(
            None,
            add_messages,
            [cleaned_content],
            [embedding],
            [message_id],
            [author]
        )
        
        if added > 0:
            log(f"[STORAGE] Stored message from {author} in database", Fore.MAGENTA)
    except Exception as e:
        log(f"[STORAGE ERROR] Failed to store message: {e}", Fore.RED)


async def store_messages_batch(messages_with_authors):
    """
    Store multiple messages in ChromaDB as a batch.
    
    Args:
        messages_with_authors: List of tuples (author, message_content)
    """
    if not messages_with_authors:
        return
    
    try:
        authors = [msg[0] for msg in messages_with_authors]
        contents = [msg[1] for msg in messages_with_authors]
        
        # Generate embeddings for all messages
        from embedding_pipeline import generate_embeddings_batch
        embeddings = await generate_embeddings_batch([(a, c) for a, c in messages_with_authors])
        
        # Generate message IDs
        message_ids = [
            hashlib.sha256(content.encode('utf-8')).hexdigest()
            for content in contents
        ]
        
        # Store in ChromaDB
        loop = asyncio.get_event_loop()
        added = await loop.run_in_executor(
            None,
            add_messages,
            contents,
            embeddings,
            message_ids,
            authors
        )
        
        log(f"[STORAGE] Stored {added} messages in database", Fore.MAGENTA)
    except Exception as e:
        log(f"[STORAGE ERROR] Failed to store batch: {e}", Fore.RED)
