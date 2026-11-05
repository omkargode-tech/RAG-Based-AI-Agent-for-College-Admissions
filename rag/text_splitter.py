from config import CHUNK_OVERLAP, CHUNK_SIZE


def split_text(text):
    """Split text into overlapping word-based chunks."""
    words = text.split()
    if not words:
        return []

    step = CHUNK_SIZE - CHUNK_OVERLAP
    chunks = []

    for start in range(0, len(words), step):
        chunk = " ".join(words[start : start + CHUNK_SIZE]).strip()
        if chunk:
            chunks.append(chunk)

        if start + CHUNK_SIZE >= len(words):
            break

    return chunks
