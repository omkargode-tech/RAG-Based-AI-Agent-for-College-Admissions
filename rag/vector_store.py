import chromadb

from config import CHROMA_DIR, COLLECTION_NAME


def get_collection():
    """Return the persistent ChromaDB collection."""
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def get_chunk_count():
    return get_collection().count()


def get_indexed_sources():
    collection = get_collection()
    if collection.count() == 0:
        return []

    result = collection.get(include=["metadatas"])
    names = {
        metadata["source"]
        for metadata in result["metadatas"]
        if metadata and metadata.get("source")
    }
    return sorted(names)
