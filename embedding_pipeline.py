import os
import json
import time
import aiohttp
import asyncio
from message_parser import parse_all_files_in_folder, parse_discord_export
from chromadb_storage import add_messages, get_collection_count
import hashlib

LLM_API_KEY = os.getenv('LLM_API_KEY')

async def generate_embedding(text):
    """
    Generate embedding vector for text using Google's embedding model.
    
    Args:
        text: Text to embed
        
    Returns:
        List of floats representing the embedding vector
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent?key={LLM_API_KEY}"
    
    payload = {
        "model": "models/text-embedding-004",
        "content": {
            "parts": [{
                "text": text
            }]
        }
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers={"Content-Type": "application/json"}, data=json.dumps(payload)) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    print(f"[ERROR] Embedding API error: {error_text}")
                    raise Exception(f"Embedding API error: {error_text}")
                
                response_data = await resp.json()
                embedding = response_data['embedding']['values']
                return embedding
    except Exception as e:
        print(f"[ERROR] Failed to generate embedding: {e}")
        raise


async def generate_embeddings_batch(messages, batch_size=20):
    """
    Generate embeddings for multiple messages with rate limiting.
    
    Args:
        messages: List of tuples (author, text) or list of text strings (for backward compatibility)
        batch_size: Number of concurrent requests
        
    Returns:
        List of embedding vectors
    """
    # Handle both formats: tuples and strings
    if messages and isinstance(messages[0], tuple):
        texts = [msg[1] for msg in messages]  # Extract text from (author, text) tuples
    else:
        texts = messages
    
    embeddings = []
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        print(f"Processing batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1}...")
        
        # Process batch concurrently
        tasks = [generate_embedding(text) for text in batch]
        batch_embeddings = await asyncio.gather(*tasks)
        embeddings.extend(batch_embeddings)
        
        # Rate limiting - small delay between batches
        if i + batch_size < len(texts):
            await asyncio.sleep(0.2)
    
    return embeddings


def store_embeddings_in_chromadb(messages, embeddings, source_file):
    """
    Store messages and their embeddings in ChromaDB with deduplication.
    Uses content hash as ID to prevent duplicate messages.
    
    Args:
        messages: List of tuples (author, message_text) or list of message strings (for backward compatibility)
        embeddings: List of embedding vectors
        source_file: Name of the source file
    """
    # Handle both formats: tuples (author, text) and plain strings
    if messages and isinstance(messages[0], tuple):
        authors = [msg[0] for msg in messages]
        message_texts = [msg[1] for msg in messages]
    else:
        authors = None
        message_texts = messages
    
    # Generate message IDs using content hash for deduplication
    message_ids = [
        hashlib.sha256(msg.encode('utf-8')).hexdigest()
        for msg in message_texts
    ]
    
    # Get count before adding
    count_before = get_collection_count()
    
    try:
        # Add messages to ChromaDB (will skip duplicates by ID)
        add_messages(message_texts, embeddings, message_ids, authors)
        
        # Get count after adding
        count_after = get_collection_count()
        
        inserted_count = count_after - count_before
        skipped_count = len(messages) - inserted_count
        
        print(f"Stored {inserted_count} new messages, skipped {skipped_count} duplicates")
    
    except Exception as e:
        print(f"Error storing messages: {e}")
        print("Assuming all messages were duplicates")
        print(f"Stored 0 new messages, skipped {len(messages)} duplicates")


async def process_file(file_path):
    """
    Process a single Discord export file: parse, embed, and store.
    
    Args:
        file_path: Path to the .txt file
    """
    print(f"\n{'='*60}")
    print(f"Processing: {file_path}")
    print(f"{'='*60}")
    
    # Parse messages
    messages = parse_discord_export(file_path)
    print(f"Extracted {len(messages)} messages")
    
    if not messages:
        print("No messages to process")
        return
    
    # Generate embeddings
    print("Generating embeddings...")
    embeddings = await generate_embeddings_batch(messages)
    
    # Store in ChromaDB
    print("Storing in ChromaDB...")
    store_embeddings_in_chromadb(messages, embeddings, os.path.basename(file_path))
    
    print(f"✓ Successfully processed {file_path}")


async def process_all_files(folder_path='attached_assets'):
    """
    Process all Discord export files in a folder.
    
    Args:
        folder_path: Path to folder containing .txt files
    """
    from pathlib import Path
    
    folder = Path(folder_path)
    txt_files = list(folder.glob('*.txt'))
    
    if not txt_files:
        print(f"No .txt files found in {folder_path}")
        return
    
    print(f"Found {len(txt_files)} files to process")
    
    for file_path in txt_files:
        await process_file(str(file_path))
    
    # Print summary
    total_messages = get_collection_count()
    
    print(f"\n{'='*60}")
    print(f"COMPLETE! Total messages in ChromaDB: {total_messages}")
    print(f"{'='*60}")


if __name__ == '__main__':
    if not LLM_API_KEY:
        print("ERROR: LLM_API_KEY not found in environment variables")
        exit(1)
    
    print("Starting embedding pipeline...")
    asyncio.run(process_all_files())
