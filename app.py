from pathlib import Path

import streamlit as st

from config import APP_TITLE, APP_SUBTITLE, DOCUMENTS_DIR
from rag.ingestion import SUPPORTED_EXTENSIONS, ingest_document
from rag.pipeline import answer_question
from rag.vector_store import get_chunk_count, get_indexed_sources

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="expanded",
)


st.markdown(
    """
    <style>
      .stApp { background: var(--background-color); }
      [data-testid="stHeader"] { background: transparent; }
      [data-testid="stSidebar"] { border-right: 1px solid var(--secondary-background-color); }
      .block-container { max-width: 880px; padding-top: 2rem; padding-bottom: 6rem; }
      .brand-title { font-size: 2.7rem; font-weight: 700; letter-spacing: -.045em; display:flex; justify-content:center; align-items:center; }
      .brand-subtitle { color: var(--text-color); opacity: .68; font-size: 1.05rem; margin-top: -.25rem; display:flex; justify-content:center; align-items:center; }
      [data-testid="stChatMessage"] { border: 1px solid var(--secondary-background-color); border-radius: 14px; }
      .stButton > button { border-radius: 9px; }
      div[data-testid="stFileUploader"] section { border: 1px dashed var(--text-color); border-opacity: .3; }
      .small-note { font-size: .82rem; opacity: .7; }
    </style>
    """,
    unsafe_allow_html=True,
)

DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.markdown("# Indala College")
    st.caption("Admission knowledge assistant")
    st.divider()

    st.markdown("**College documents**")
    uploads = st.file_uploader(
        "Upload official documents",
        type=["pdf", "docx", "txt", "md"],
        accept_multiple_files=True,
        help="Supported formats: PDF, Word (.docx), text (.txt), and Markdown (.md).",
        key="college_document_uploader",
    )

    process_clicked = st.button(
        "Save and process documents",
        use_container_width=True,
        disabled=not uploads,
        type="primary",
    )
    if process_clicked and uploads:
        progress = st.progress(0)
        status = st.empty()
        successes = 0
        failures = []
        for index, uploaded_file in enumerate(uploads, start=1):
            safe_name = Path(uploaded_file.name).name
            suffix = Path(safe_name).suffix.lower()
            if suffix not in SUPPORTED_EXTENSIONS:
                failures.append(f"{safe_name}: unsupported file type")
                progress.progress(index / len(uploads))
                continue

            destination = DOCUMENTS_DIR / safe_name
            try:
                destination.write_bytes(uploaded_file.getvalue())
                status.write(f"Processing {safe_name}…")
                result = ingest_document(destination)
                successes += 1
                status.write(
                    f"{safe_name}: {result['chunks']} chunks — {result['status']}"
                )
            except Exception as exc:
                failures.append(f"{safe_name}: {exc}")
            progress.progress(index / len(uploads))

        if successes:
            st.success(f"Processed {successes} document(s).")
        if failures:
            for failure in failures:
                st.error(failure)
        st.rerun()

    st.divider()
    st.markdown("**Knowledge base**")
    st.metric("Indexed chunks", get_chunk_count())

    indexed_sources = get_indexed_sources()
    source_options = ["All documents", *indexed_sources]
    selected_source = st.selectbox(
        "Search within",
        source_options,
        key="source_filter",
    )
    st.caption("Answers are grounded in the indexed college documents.")

    if st.button("Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

st.markdown(f'<div class="brand-title">{APP_TITLE}</div>', unsafe_allow_html=True)
st.markdown(
    f'<div class="brand-subtitle">{APP_SUBTITLE}</div>',
    unsafe_allow_html=True,
)
st.write("")

# if not st.session_state.messages:
#     st.markdown("#### Welcome!")
#     st.write(
#         "Ask questions about Indala College using its official uploaded documents. "
#         "I will identify the source location and say when the documents do not contain an answer."
#     )
#     st.markdown(
#         "- Courses and course details\n"
#         "- Eligibility criteria and required documents\n"
#         "- Fees and admission procedures\n"
#         "- Important dates and contact information"
#     )
#     st.caption("Supported source files: PDF, DOCX, TXT and Markdown.")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("sources"):
            with st.expander("Sources used"):
                for item in message["sources"]:
                    st.markdown(f"- **{item['source']}** — {item['location']}")

question = st.chat_input("Ask an admission question…")
if question and question.strip():
    question = question.strip()
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    source_filter = None if selected_source == "All documents" else selected_source
    with st.chat_message("assistant"):
        with st.spinner("Searching college documents…"):
            try:
                result = answer_question(question, source=source_filter)
                answer = result.get("answer") or "I couldn't generate an answer. Please try again."
                sources = result.get("sources", [])
                st.markdown(answer)
                if sources:
                    with st.expander("Sources used", expanded=True):
                        for item in sources:
                            st.markdown(f"- **{item['source']}** — {item['location']}")
                st.session_state.messages.append(
                    {"role": "assistant", "content": answer, "sources": sources}
                )
            except Exception as exc:
                # Keep the user-facing error actionable without exposing stack traces.
                error_text = (
                    "I couldn't complete that request. Please check the Groq API key, "
                    "model name, internet connection, and application logs."
                )
                st.error(error_text)
                with st.expander("Technical details"):
                    st.code(str(exc))
                st.session_state.messages.append(
                    {"role": "assistant", "content": error_text, "sources": []}
                )
