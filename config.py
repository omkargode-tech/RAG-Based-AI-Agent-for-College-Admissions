import os
from pathlib import Path

from dotenv import load_dotenv

# Load values from the project's .env file.
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# App settings
APP_TITLE = os.getenv("APP_TITLE", "Indala College")
APP_SUBTITLE = os.getenv(
    "APP_SUBTITLE",
    "Admission Assistant · Ask about courses, eligibility, fees and admissions.",
)

# Paths
DOCUMENTS_DIR = BASE_DIR / os.getenv("DOCUMENTS_DIR", os.getenv("PDF_DIR", "data/college_docs"))
PDF_DIR = DOCUMENTS_DIR  # Backward-compatible alias
CHROMA_DIR = BASE_DIR / os.getenv("CHROMA_DIR", "chroma_db")

# Groq settings
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GROQ_BASE_URL = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
GROQ_MODEL = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")

# Embedding settings
EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "sentence-transformers/all-MiniLM-L6-v2",
)

# Retrieval and chunking settings
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "220"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "45"))
TOP_K = int(os.getenv("TOP_K", "5"))
EMBED_BATCH_SIZE = int(os.getenv("EMBED_BATCH_SIZE", "32"))
COLLECTION_NAME = os.getenv(
    "COLLECTION_NAME",
    "indala_college_knowledge",
)

# Generation settings
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.1"))
MAX_COMPLETION_TOKENS = int(os.getenv("MAX_COMPLETION_TOKENS", "1200"))

# Basic configuration validation.
if CHUNK_SIZE <= 0:
    raise ValueError("CHUNK_SIZE must be greater than zero.")
if CHUNK_OVERLAP < 0 or CHUNK_OVERLAP >= CHUNK_SIZE:
    raise ValueError("CHUNK_OVERLAP must be >= 0 and smaller than CHUNK_SIZE.")
if TOP_K <= 0:
    raise ValueError("TOP_K must be greater than zero.")
