from pathlib import Path

from pypdf import PdfReader


def extract_pdf_pages(pdf_path):
    """
    Extract text page by page.

    Returns a list of dictionaries with 1-based page numbers and page text.
    Pages with no extractable text are skipped.
    """
    path = Path(pdf_path)
    if not path.is_file():
        raise FileNotFoundError(f"PDF file not found: {path}")

    reader = PdfReader(str(path))
    extracted_pages = []

    for page_index, page in enumerate(reader.pages):
        text = (page.extract_text() or "").strip()
        if text:
            extracted_pages.append(
                {
                    "page": page_index + 1,
                    "text": text,
                }
            )

    return extracted_pages, len(reader.pages)
