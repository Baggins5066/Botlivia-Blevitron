import os
import json
import asyncpg
import aiohttp

LLM_API_KEY = os.getenv('LLM_API_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')

# Reusable aiohttp session for efficiency
_http_session = None

async def get_http_session():
    """Get or create a persistent aiohttp session"""
    global _http_session
    if _http_session is None or _http_session.closed:
        _http_session = aiohttp.ClientSession()
    return _http_session

async def generate_query_embedding(query_text):
    """
    Generate embedding for a query text using Google's embedding model.
    Uses persistent HTTP session for efficiency.
    
    Args:
        query_text: The text to embed
        
    Returns:
        List of floats representing the embedding vector
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent?key={LLM_API_KEY}"
    
    payload = {
        "model": "models/text-embedding-004",
        "content": {
            "parts": [{
                "text": query_text
            }]
        }
    }
    
    session = await get_http_session()
    async with session.post(url, headers={"Content-Type": "application/json"}, data=json.dumps(payload)) as resp:
        if resp.status != 200:
            error_text = await resp.text()
            raise Exception(f"Embedding API error: {error_text}")
        
        response_data = await resp.json()
        embedding = response_data['embedding']['values']
        return embedding


async def search_similar_messages(query_text, limit=8):
    """
    Search for messages similar to the query text using vector similarity.
    Uses async database operations to avoid blocking the event loop.
    
    Args:
        query_text: The text to search for
        limit: Maximum number of results to return (default 8)
        
    Returns:
        List of tuples (message_content, similarity_score)
    """
    try:
        # Generate embedding for the query
        query_embedding = await generate_query_embedding(query_text)
        
        # Convert embedding list to PostgreSQL vector format string
        vector_str = '[' + ','.join(map(str, query_embedding)) + ']'
        
        # Connect to database with asyncpg
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Perform vector similarity search using cosine distance
        results = await conn.fetch(
            """
            SELECT content, 1 - (embedding <=> $1::vector) as similarity
            FROM message_embeddings
            WHERE embedding IS NOT NULL
            ORDER BY embedding <=> $1::vector
            LIMIT $2
            """,
            vector_str, limit
        )
        
        await conn.close()
        
        # Convert asyncpg Records to tuples
        return [(row['content'], row['similarity']) for row in results]
    
    except Exception as e:
        print(f"Error in search_similar_messages: {e}")
        return []


async def get_relevant_memories(current_message, conversation_history, limit=5):
    """
    Get relevant memories based on current message and recent conversation.
    
    Args:
        current_message: The current message text
        conversation_history: List of recent messages for context
        limit: Number of memories to retrieve
        
    Returns:
        List of relevant message strings
    """
    # Combine current message with recent context for better search
    context = " ".join([msg.get('content', '') for msg in conversation_history[-3:]])
    search_query = f"{context} {current_message}"
    
    # Search for similar messages
    results = await search_similar_messages(search_query, limit)
    
    # Extract just the message content
    memories = [content for content, similarity in results if similarity > 0.3]
    
    return memories


if __name__ == '__main__':
    # Test the search function
    import asyncio
    
    async def test():
        test_query = "what do you want to do tonight? want to play valorant?"
        print(f"Searching for messages similar to: '{test_query}'\n")
        
        results = await search_similar_messages(test_query, limit=5)
        
        print(f"Found {len(results)} similar messages:\n")
        for i, (content, similarity) in enumerate(results, 1):
            print(f"{i}. [Similarity: {similarity:.3f}] {content}")
    
    asyncio.run(test())
