# Indala College Admission Chatbot

A RAG-based AI chatbot built to help students get information about Indala College admissions. Students can ask questions about courses, eligibility, fees, admission procedures, and other college-related information.

## Features

- Chat with AI about college admissions.
- Get answers from uploaded college documents.
- Supports PDF documents.
- Provides source references with answers.
- Uses ChromaDB for storing document embeddings.
- Uses Sentence Transformers for semantic search.
- Simple ChatGPT-like interface built with Streamlit.
- Uses Groq API for generating responses.

## Tech Stack

- Python
- Streamlit
- ChromaDB
- Sentence Transformers
- Groq API

## Installation

**1. Clone the repository**

```bash
git clone https://github.com/omkargode-tech/RAG-Based-AI-Agent-for-College-Admissions
cd RAG-Based-AI-Agent-for-College-Admissions
```

**2. Create a virtual environment**

```bash
python -m venv venv
```

**3. Activate the environment**

```bash
venv\Scripts\activate
```

**4. Install dependencies**

```bash
pip install -r requirements.txt
```

**5. Set up environment variables**

Create a `.env` file and add your Groq API key:

```env
GROQ_API_KEY=your_groq_api_key
```

**6. Run the application**

```bash
streamlit run app.py
```

## Note

The chatbot answers based on the available college documents. If the required information is not found, it avoids making up answers.

---
