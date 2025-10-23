"""
ChromaDB storage module for local vector database.
Stores message embeddings in the project directory instead of PostgreSQL.
"""

import chromadb
from chromadb.config import Settings
import os

CHROMA_DATA_DIR = "./chroma_data"
COLLECTION_NAME = "discord_messages"


def get_chromadb_client():
    """
    Get or create ChromaDB client with local persistent storage.
    
    Returns:
        chromadb.Client: ChromaDB client instance
    """
    client = chromadb.PersistentClient(
        path=CHROMA_DATA_DIR,
        settings=Settings(
            anonymized_telemetry=False,
            allow_reset=True
        )
    )
    return client


def get_or_create_collection():
    """
    Get or create the collection for storing message embeddings.
    Uses cosine similarity for vector search.
    
    Returns:
        chromadb.Collection: ChromaDB collection instance
    """
    client = get_chromadb_client()
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}  # Use cosine similarity
    )
    return collection


def add_messages(messages, embeddings, message_ids=None):
    """
    Add messages and their embeddings to ChromaDB with proper deduplication.
    Filters out duplicates and only adds new messages.
    
    Args:
        messages: List of message text content
        embeddings: List of embedding vectors (must match length of messages)
        message_ids: Optional list of IDs (will auto-generate if not provided)
        
    Returns:
        int: Number of messages added (excludes duplicates)
    """
    if not messages or not embeddings:
        return 0
    
    if len(messages) != len(embeddings):
        raise ValueError("Messages and embeddings must have same length")
    
    collection = get_or_create_collection()
    
    # Generate IDs if not provided
    if message_ids is None:
        import hashlib
        message_ids = [
            hashlib.sha256(msg.encode('utf-8')).hexdigest()
            for msg in messages
        ]
    
    # First pass: deduplicate within batch and build mapping
    id_to_first_occurrence = {}
    for i, msg_id in enumerate(message_ids):
        if msg_id not in id_to_first_occurrence:
            id_to_first_occurrence[msg_id] = i
    
    # Query ChromaDB with deduplicated IDs to check which exist
    unique_ids = list(id_to_first_occurrence.keys())
    try:
        existing_data = collection.get(ids=unique_ids, include=[])
        existing_ids = set(existing_data['ids']) if existing_data and 'ids' in existing_data else set()
    except Exception:
        existing_ids = set()
    
    # Second pass: build list of truly new messages
    new_messages = []
    new_embeddings = []
    new_ids = []
    
    for msg_id, index in id_to_first_occurrence.items():
        # Only add if not already in database
        if msg_id not in existing_ids:
            new_messages.append(messages[index])
            new_embeddings.append(embeddings[index])
            new_ids.append(msg_id)
    
    # If no new messages, return early
    if not new_messages:
        return 0
    
    # ChromaDB expects embeddings as list of lists
    if new_embeddings and isinstance(new_embeddings[0], list):
        embedding_list = new_embeddings
    else:
        embedding_list = [emb.tolist() if hasattr(emb, 'tolist') else list(emb) for emb in new_embeddings]
    
    try:
        # Add only new messages to collection
        collection.add(
            ids=new_ids,
            embeddings=embedding_list,
            documents=new_messages,
            metadatas=[{"text": msg} for msg in new_messages]
        )
        return len(new_messages)
    except Exception as e:
        print(f"Error adding messages to ChromaDB: {e}")
        return 0


def search_similar_messages(query_embedding, limit=8):
    """
    Search for messages similar to the query embedding.
    
    Args:
        query_embedding: The embedding vector to search for
        limit: Maximum number of results to return
        
    Returns:
        List of tuples (message_content, similarity_score)
    """
    collection = get_or_create_collection()
    
    # Convert embedding to list if needed
    if hasattr(query_embedding, 'tolist'):
        query_embedding = query_embedding.tolist()
    elif not isinstance(query_embedding, list):
        query_embedding = list(query_embedding)
    
    try:
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=limit,
            include=["documents", "distances"]
        )
        
        # Convert results to list of tuples (message, similarity)
        # ChromaDB returns distances, we convert to similarity (1 - distance)
        messages = results['documents'][0] if results['documents'] else []
        distances = results['distances'][0] if results['distances'] else []
        
        # Convert distance to similarity score (cosine similarity)
        similarities = [(msg, 1 - dist) for msg, dist in zip(messages, distances)]
        
        return similarities
    
    except Exception as e:
        print(f"Error in search_similar_messages: {e}")
        return []


def get_collection_count():
    """
    Get the number of messages in the collection.
    
    Returns:
        int: Number of messages stored
    """
    try:
        collection = get_or_create_collection()
        return collection.count()
    except Exception as e:
        print(f"[ERROR] Failed to get collection count: {e}")
        return 0


def reset_collection():
    """
    Reset (delete) the collection. Use with caution!
    """
    client = get_chromadb_client()
    try:
        client.delete_collection(name=COLLECTION_NAME)
        print(f"Collection '{COLLECTION_NAME}' deleted successfully")
    except Exception as e:
        print(f"Error deleting collection: {e}")
