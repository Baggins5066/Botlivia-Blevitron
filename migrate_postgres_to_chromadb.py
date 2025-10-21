"""
Migration script to transfer message embeddings from PostgreSQL to ChromaDB.
This is a one-time migration to move your existing data to local file-based storage.
"""

import os
import psycopg2
from pgvector.psycopg2 import register_vector
import numpy as np
from chromadb_storage import add_messages, get_collection_count, reset_collection
import hashlib

DATABASE_URL = os.getenv('DATABASE_URL')


def migrate_postgres_to_chromadb():
    """
    Migrate all message embeddings from PostgreSQL to ChromaDB.
    """
    print("Starting migration from PostgreSQL to ChromaDB...")
    print("=" * 60)
    
    if not DATABASE_URL:
        print("ERROR: DATABASE_URL not found in environment variables")
        print("Make sure PostgreSQL database is available")
        return
    
    # Connect to PostgreSQL
    print("\n1. Connecting to PostgreSQL...")
    conn = psycopg2.connect(DATABASE_URL)
    register_vector(conn)
    cursor = conn.cursor()
    
    # Get total count
    cursor.execute("SELECT COUNT(*) FROM message_embeddings WHERE embedding IS NOT NULL")
    total_count = cursor.fetchone()[0]
    print(f"   Found {total_count} messages in PostgreSQL")
    
    # Fetch all messages and embeddings
    print("\n2. Fetching messages and embeddings...")
    cursor.execute("""
        SELECT content, embedding 
        FROM message_embeddings 
        WHERE embedding IS NOT NULL
    """)
    
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    
    print(f"   Retrieved {len(rows)} messages")
    
    if not rows:
        print("\n   No data to migrate!")
        return
    
    # Prepare data for ChromaDB
    print("\n3. Preparing data for ChromaDB...")
    messages = []
    embeddings = []
    message_ids = []
    
    for content, embedding in rows:
        messages.append(content)
        # Convert pgvector to list
        if isinstance(embedding, str):
            # Parse string format if needed
            embedding = [float(x) for x in embedding.strip('[]').split(',')]
        elif hasattr(embedding, 'tolist'):
            embedding = embedding.tolist()
        elif not isinstance(embedding, list):
            embedding = list(embedding)
        
        embeddings.append(embedding)
        
        # Generate ID from content hash
        content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
        message_ids.append(content_hash)
    
    print(f"   Prepared {len(messages)} messages for migration")
    
    # Check if ChromaDB already has data
    existing_count = get_collection_count()
    if existing_count > 0:
        print(f"\n   WARNING: ChromaDB already contains {existing_count} messages")
        response = input("   Do you want to reset ChromaDB before migration? (yes/no): ")
        if response.lower() == 'yes':
            reset_collection()
            print("   ChromaDB collection reset")
    
    # Migrate to ChromaDB in batches
    print("\n4. Migrating to ChromaDB...")
    batch_size = 100
    migrated_count = 0
    
    for i in range(0, len(messages), batch_size):
        batch_messages = messages[i:i+batch_size]
        batch_embeddings = embeddings[i:i+batch_size]
        batch_ids = message_ids[i:i+batch_size]
        
        # Deduplicate within the batch itself
        seen_ids = {}
        dedup_messages = []
        dedup_embeddings = []
        dedup_ids = []
        
        for j, msg_id in enumerate(batch_ids):
            if msg_id not in seen_ids:
                seen_ids[msg_id] = True
                dedup_messages.append(batch_messages[j])
                dedup_embeddings.append(batch_embeddings[j])
                dedup_ids.append(msg_id)
        
        if dedup_messages:
            try:
                added = add_messages(dedup_messages, dedup_embeddings, dedup_ids)
                migrated_count += added
                print(f"   Migrated {migrated_count} unique messages so far...")
            except Exception as e:
                print(f"   Error migrating batch: {e}")
                continue
    
    # Verify migration
    print("\n5. Verifying migration...")
    final_count = get_collection_count()
    print(f"   ChromaDB now contains {final_count} messages")
    
    print("\n" + "=" * 60)
    print(f"MIGRATION COMPLETE!")
    print(f"  PostgreSQL: {total_count} messages")
    print(f"  ChromaDB:   {final_count} messages")
    print("=" * 60)
    
    if final_count == total_count:
        print("\n✓ All messages migrated successfully!")
    else:
        print(f"\n⚠ Warning: Migrated {final_count}/{total_count} messages")
        print("  Some duplicates may have been skipped")


if __name__ == '__main__':
    migrate_postgres_to_chromadb()
