"""
Check how many messages in ChromaDB contain user ID mentions.
"""

import re
from chromadb_storage import get_or_create_collection

def check_mentions():
    """Check for user mentions in message content."""
    collection = get_or_create_collection()
    
    # Get all messages (or a large sample)
    total_count = collection.count()
    sample_size = min(total_count, 200)
    
    results = collection.get(limit=sample_size, include=["documents", "metadatas"])
    
    if not results or not results.get('documents'):
        print("No messages found in database")
        return
    
    documents = results['documents']
    metadatas = results['metadatas']
    
    print(f"Checking {len(documents)} messages out of {total_count} total:\n")
    
    # Pattern for user mentions
    mention_pattern = r'<@!?\d+>'
    
    messages_with_mentions = []
    
    for i, doc in enumerate(documents):
        if re.search(mention_pattern, doc):
            author = metadatas[i].get('author', 'Unknown') if i < len(metadatas) and metadatas[i] else 'Unknown'
            messages_with_mentions.append((author, doc))
    
    print(f"Statistics:")
    print(f"  Total messages checked: {len(documents)}")
    print(f"  Messages with user mentions: {len(messages_with_mentions)}")
    print(f"  Percentage: {len(messages_with_mentions)/len(documents)*100:.1f}%")
    
    if messages_with_mentions:
        print(f"\nSample messages with mentions (showing first 5):")
        for author, msg in messages_with_mentions[:5]:
            # Truncate long messages
            msg_preview = msg[:100] + "..." if len(msg) > 100 else msg
            print(f"  [{author}]: {msg_preview}")

if __name__ == '__main__':
    check_mentions()
