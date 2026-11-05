from functools import lru_cache

from sentence_transformers import SentenceTransformer

from config import EMBEDDING_MODEL, EMBED_BATCH_SIZE


@lru_cache(maxsize=1)
def get_embedding_model():
    """Load the local Sentence Transformer once per Python process."""
    return SentenceTransformer(EMBEDDING_MODEL)


def embed_texts(texts):
    """Embed a list of text chunks in batches."""
    if not texts:
        return []

    model = get_embedding_model()
    vectors = []

    for start in range(0, len(texts), EMBED_BATCH_SIZE):
        batch = texts[start : start + EMBED_BATCH_SIZE]
        batch_vectors = model.encode(
            batch,
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False,
        )
        vectors.extend(batch_vectors.tolist())

    return vectors


def embed_query(question):
    """Embed one student question."""
    model = get_embedding_model()
    vector = model.encode(
        question,
        normalize_embeddings=True,
        convert_to_numpy=True,
    )
    return vector.tolist()
