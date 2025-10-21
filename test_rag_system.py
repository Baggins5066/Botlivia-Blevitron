import asyncio
import psycopg2
from pgvector.psycopg2 import register_vector
from memory_search import search_similar_messages, get_relevant_memories
import os

DATABASE_URL = os.getenv('DATABASE_URL')

async def test_rag_system():
    print("="*60)
    print("RAG SYSTEM TEST")
    print("="*60)
    
    # Test 1: Database connectivity
    print("\n1. Testing database connectivity...")
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM message_embeddings")
        count = cursor.fetchone()[0]
        print(f"   ✓ Connected to database")
        print(f"   ✓ Found {count} messages with embeddings")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"   ✗ Database error: {e}")
        return
    
    # Test 2: Search for similar messages
    print("\n2. Testing semantic search...")
    test_queries = [
        "what do you want to do tonight?",
        "im trying to work",
        "join voice chat",
        "are you feeling awkward?"
    ]
    
    for query in test_queries:
        print(f"\n   Query: '{query}'")
        results = await search_similar_messages(query, limit=3)
        if results:
            print(f"   Found {len(results)} similar messages:")
            for content, similarity in results:
                print(f"     - [similarity: {similarity:.3f}] {content[:60]}...")
        else:
            print("   ✗ No results found")
    
    # Test 3: Test get_relevant_memories function
    print("\n3. Testing memory retrieval with conversation context...")
    conversation = [
        {"author": "User", "content": "hey what's up"},
        {"author": "Bot", "content": "not much, just chilling"},
        {"author": "User", "content": "want to play valorant later?"}
    ]
    current_msg = "yeah let's play some games"
    
    memories = await get_relevant_memories(current_msg, conversation, limit=5)
    print(f"   Retrieved {len(memories)} relevant memories:")
    for i, mem in enumerate(memories, 1):
        print(f"   {i}. {mem[:80]}...")
    
    # Test 4: Verify embeddings quality
    print("\n4. Testing embedding quality...")
    conn = psycopg2.connect(DATABASE_URL)
    register_vector(conn)
    cursor = conn.cursor()
    cursor.execute("SELECT content, embedding FROM message_embeddings LIMIT 1")
    sample = cursor.fetchone()
    if sample:
        content, embedding = sample
        print(f"   Sample message: '{content[:60]}...'")
        print(f"   Embedding dimensions: {len(embedding)}")
        print(f"   Embedding type: {type(embedding)}")
    cursor.close()
    conn.close()
    
    print("\n" + "="*60)
    print("TEST COMPLETE ✓")
    print("="*60)

if __name__ == '__main__':
    asyncio.run(test_rag_system())
