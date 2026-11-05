from typing import Optional

from config import TOP_K
from rag.embeddings import embed_query
from rag.vector_store import get_collection


def retrieve(question: str, top_k: int = TOP_K, source: Optional[str] = None):
    """Retrieve the most relevant chunks from ChromaDB."""
    collection = get_collection()
    total_chunks = collection.count()

    if total_chunks == 0:
        return []

    query_args = {
        "query_embeddings": [embed_query(question)],
        "n_results": min(top_k, total_chunks),
        "include": ["documents", "metadatas", "distances"],
    }

    if source:
        query_args["where"] = {"source": source}

    results = collection.query(**query_args)
    retrieved = []

    for text, metadata, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        retrieved.append(
            {
                "text": text,
                "metadata": metadata,
                "distance": float(distance),
            }
        )

    return retrieved
