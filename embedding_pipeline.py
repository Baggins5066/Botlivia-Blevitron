import os
import json
import time
import psycopg2
from psycopg2.extras import execute_values
from pgvector.psycopg2 import register_vector
import aiohttp
import asyncio
from message_parser import parse_all_files_in_folder, parse_discord_export

LLM_API_KEY = os.getenv('LLM_API_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')

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
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers={"Content-Type": "application/json"}, data=json.dumps(payload)) as resp:
            if resp.status != 200:
                error_text = await resp.text()
                raise Exception(f"Embedding API error: {error_text}")
            
            response_data = await resp.json()
            embedding = response_data['embedding']['values']
            return embedding


async def generate_embeddings_batch(texts, batch_size=20):
    """
    Generate embeddings for multiple texts with rate limiting.
    
    Args:
        texts: List of text strings
        batch_size: Number of concurrent requests
        
    Returns:
        List of embedding vectors
    """
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


def store_embeddings_in_db(messages, embeddings, source_file):
    """
    Store messages and their embeddings in PostgreSQL with deduplication.
    Uses content hash to prevent duplicate messages from being inserted.
    
    Args:
        messages: List of message strings
        embeddings: List of embedding vectors
        source_file: Name of the source file
    """
    import hashlib
    
    conn = psycopg2.connect(DATABASE_URL)
    register_vector(conn)
    cursor = conn.cursor()
    
    # Create content_hash column if it doesn't exist
    cursor.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name='message_embeddings' AND column_name='content_hash'
            ) THEN
                ALTER TABLE message_embeddings ADD COLUMN content_hash VARCHAR(64) UNIQUE;
                CREATE INDEX IF NOT EXISTS idx_content_hash ON message_embeddings(content_hash);
            END IF;
        END $$;
    """)
    conn.commit()
    
    # Insert messages with ON CONFLICT to skip duplicates
    inserted_count = 0
    skipped_count = 0
    
    for msg, emb in zip(messages, embeddings):
        # Generate content hash
        content_hash = hashlib.sha256(msg.encode('utf-8')).hexdigest()
        
        try:
            cursor.execute(
                """
                INSERT INTO message_embeddings (content, embedding, source_file, content_hash)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (content_hash) DO NOTHING
                """,
                (msg, emb, source_file, content_hash)
            )
            if cursor.rowcount > 0:
                inserted_count += 1
            else:
                skipped_count += 1
        except Exception as e:
            print(f"Error inserting message: {e}")
            skipped_count += 1
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"Stored {inserted_count} new messages, skipped {skipped_count} duplicates")


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
    
    # Store in database
    print("Storing in database...")
    store_embeddings_in_db(messages, embeddings, os.path.basename(file_path))
    
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
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM message_embeddings")
    total_messages = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    
    print(f"\n{'='*60}")
    print(f"COMPLETE! Total messages in database: {total_messages}")
    print(f"{'='*60}")


if __name__ == '__main__':
    if not LLM_API_KEY:
        print("ERROR: LLM_API_KEY not found in environment variables")
        exit(1)
    
    if not DATABASE_URL:
        print("ERROR: DATABASE_URL not found in environment variables")
        exit(1)
    
    print("Starting embedding pipeline...")
    asyncio.run(process_all_files())
