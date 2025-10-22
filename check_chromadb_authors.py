"""
Utility script to check the author names in ChromaDB.
"""

from chromadb_storage import get_or_create_collection

def check_authors():
    """Check a sample of authors in the database."""
    collection = get_or_create_collection()
    
    # Get a sample of messages
    results = collection.get(limit=50, include=["metadatas", "documents"])
    
    if not results or not results.get('metadatas'):
        print("No messages found in database")
        return
    
    metadatas = results['metadatas']
    documents = results['documents']
    
    print(f"Checking {len(metadatas)} sample messages:\n")
    
    # Count author name patterns
    user_id_authors = []
    clean_authors = []
    no_author = []
    
    for i, metadata in enumerate(metadatas):
        if not metadata:
            no_author.append(i)
            continue
            
        author = metadata.get('author')
        if not author:
            no_author.append(i)
        elif '<@' in author or author.isdigit():
            user_id_authors.append((author, documents[i][:50] if i < len(documents) else ""))
        else:
            clean_authors.append(author)
    
    print(f"Statistics:")
    print(f"  Clean author names: {len(clean_authors)}")
    print(f"  User ID authors: {len(user_id_authors)}")
    print(f"  No author info: {len(no_author)}")
    
    if user_id_authors:
        print(f"\nSample of problematic authors (showing first 10):")
        for author, msg_preview in user_id_authors[:10]:
            print(f"  - Author: '{author}' | Message: '{msg_preview}...'")
    
    if clean_authors:
        print(f"\nSample of clean authors (showing first 10):")
        unique_clean = list(set(clean_authors))[:10]
        for author in unique_clean:
            print(f"  - {author}")

if __name__ == '__main__':
    check_authors()
