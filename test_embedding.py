import asyncio
from embedding_pipeline import generate_embedding

async def test():
    test_message = "what do you want to do tonight?"
    print(f"Testing embedding for: '{test_message}'")
    
    embedding = await generate_embedding(test_message)
    print(f"Embedding dimensions: {len(embedding)}")
    print(f"First 10 values: {embedding[:10]}")

if __name__ == '__main__':
    asyncio.run(test())
