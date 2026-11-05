import hashlib
import os
from pathlib import Path

from config import EMBED_BATCH_SIZE
from rag.document_extractor import extract_document
from rag.embeddings import embed_texts
from rag.text_splitter import split_text
from rag.vector_store import get_collection

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}


def sha256_file(file_path):
    digest = hashlib.sha256()
    with open(file_path, "rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def build_document_records(file_path):
    """Extract, chunk and attach source metadata to one supported document."""
    path = Path(file_path).resolve()
    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported format: {path.suffix}")

    file_hash = sha256_file(path)
    stat = os.stat(path)
    document_id = hashlib.sha256(str(path).encode("utf-8")).hexdigest()
    segments = extract_document(path)
    records = []

    for segment_number, segment in enumerate(segments):
        for chunk_number, chunk in enumerate(split_text(segment["text"])):
            chunk_id = (
                f"{document_id}_{file_hash[:16]}_"
                f"s{segment_number}_c{chunk_number}"
            )
            records.append(
                {
                    "id": chunk_id,
                    "text": chunk,
                    "metadata": {
                        "source": path.name,
                        "source_path": str(path),
                        "document_id": document_id,
                        "document_hash": file_hash,
                        "title": path.stem,
                        "file_type": path.suffix.lower().lstrip("."),
                        "location": segment["location"],
                        "page": segment["page"] or 0,
                        "segment": segment_number,
                        "chunk": chunk_number,
                        "file_size_bytes": stat.st_size,
                        "modified_time": float(stat.st_mtime),
                    },
                }
            )

    return records, len(segments), file_hash


def ingest_document(file_path):
    """Index a document, preserving the old version if indexing fails."""
    path = Path(file_path).resolve()
    if not path.is_file():
        raise FileNotFoundError(path)

    records, segment_count, file_hash = build_document_records(path)
    if not records:
        raise ValueError("No text chunks were created from this document.")

    collection = get_collection()
    previous = collection.get(
        where={"source_path": str(path)},
        include=["metadatas"],
    )
    previous_ids = previous.get("ids", [])

    # Avoid re-embedding an unchanged file.
    if previous.get("metadatas") and all(
        metadata.get("document_hash") == file_hash
        for metadata in previous["metadatas"]
    ):
        return {
            "source": path.name,
            "segments": segment_count,
            "chunks": len(previous_ids),
            "status": "already indexed (unchanged)",
        }

    vectors = embed_texts([record["text"] for record in records])
    # Add new hash-based IDs first. Only remove the previous version after all
    # new batches have been added successfully.
    try:
        for start in range(0, len(records), EMBED_BATCH_SIZE):
            batch = records[start : start + EMBED_BATCH_SIZE]
            end = start + len(batch)
            collection.add(
                ids=[item["id"] for item in batch],
                documents=[item["text"] for item in batch],
                embeddings=vectors[start:end],
                metadatas=[item["metadata"] for item in batch],
            )
    except Exception:
        # Remove any partially-added new records, leaving the old records intact.
        new_ids = [item["id"] for item in records]
        collection.delete(ids=new_ids)
        raise

    if previous_ids:
        collection.delete(ids=previous_ids)

    return {
        "source": path.name,
        "segments": segment_count,
        "chunks": len(records),
        "status": "indexed",
    }


def ingest_pdf(pdf_path):
    """Backward-compatible alias for older app code."""
    return ingest_document(pdf_path)
