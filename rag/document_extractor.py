"""Text extraction for supported college document formats."""
from pathlib import Path

from pypdf import PdfReader
from docx import Document


def _group_text_units(units, max_words=450):
    """Group paragraphs/lines while retaining a useful source locator."""
    groups = []
    current_text = []
    current_words = 0
    first_number = None
    last_number = None

    for number, value in units:
        value = (value or "").strip()
        if not value:
            continue
        word_count = len(value.split())
        if current_text and current_words + word_count > max_words:
            groups.append((first_number, last_number, "\n".join(current_text)))
            current_text = []
            current_words = 0
            first_number = None
            last_number = None

        if first_number is None:
            first_number = number
        last_number = number
        current_text.append(value)
        current_words += word_count

    if current_text:
        groups.append((first_number, last_number, "\n".join(current_text)))
    return groups


def extract_pdf(path):
    path = Path(path)
    reader = PdfReader(str(path))
    segments = []
    for index, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
        if text:
            segments.append({"location": f"Page {index}", "page": index, "text": text})
    return segments


def extract_docx(path):
    document = Document(str(path))
    segments = []
    paragraphs = [p.text.strip() for p in document.paragraphs if p.text.strip()]
    for start, end, text in _group_text_units(enumerate(paragraphs, start=1)):
        segments.append({
            "location": f"Paragraphs {start}-{end}",
            "page": None,
            "text": text,
        })

    # Fee structures and admission criteria are often stored in Word tables.
    for table_number, table in enumerate(document.tables, start=1):
        rows = []
        for row_number, row in enumerate(table.rows, start=1):
            cells = [cell.text.strip().replace("\n", " / ") for cell in row.cells]
            row_text = " | ".join(value for value in cells if value)
            if row_text:
                rows.append((row_number, row_text))
        for start, end, text in _group_text_units(rows):
            segments.append({
                "location": f"Table {table_number}, rows {start}-{end}",
                "page": None,
                "text": text,
            })
    return segments


def extract_text_file(path):
    path = Path(path)
    # utf-8-sig also handles a UTF-8 BOM. Replace malformed bytes rather than
    # failing the entire ingestion for a mostly readable text document.
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    lines = text.splitlines()
    groups = _group_text_units(enumerate(lines, start=1))
    return [
        {
            "location": f"Lines {start}-{end}",
            "page": None,
            "text": content,
        }
        for start, end, content in groups
    ]


def extract_document(file_path):
    """Return text segments with page/paragraph/line source locations."""
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"Document not found: {path}")

    suffix = path.suffix.lower()
    if suffix == ".pdf":
        segments = extract_pdf(path)
    elif suffix == ".docx":
        segments = extract_docx(path)
    elif suffix in {".txt", ".md"}:
        segments = extract_text_file(path)
    else:
        raise ValueError(
            f"Unsupported file type '{suffix}'. Supported formats: PDF, DOCX, TXT, MD."
        )

    if not segments:
        raise ValueError(
            "No readable text was extracted. If this is a scanned PDF, run OCR first."
        )
    return segments
