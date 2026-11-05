from rag.generation import generate_answer
from rag.retrieval import retrieve


def answer_question(question, source=None):
    """Run retrieval and grounded answer generation."""
    results = retrieve(question, source=source)
    if not results:
        return {
            "answer": (
                "I couldn't find relevant information in the indexed college "
                "documents. Please upload and process the official documents, "
                "or try asking the question another way."
            ),
            "sources": [],
        }

    context_blocks = []
    sources = []
    seen_sources = set()
    for item in results:
        metadata = item["metadata"]
        filename = metadata.get("source", "Unknown document")
        location = metadata.get("location") or (
            f"Page {metadata['page']}" if metadata.get("page") else "Location unavailable"
        )
        context_blocks.append(f"[Source: {filename}, {location}]\n{item['text']}")
        source_key = (filename, location)
        if source_key not in seen_sources:
            seen_sources.add(source_key)
            sources.append({"source": filename, "location": location})

    answer = generate_answer(question, "\n\n---\n\n".join(context_blocks))
    return {"answer": answer, "sources": sources}
