[English](README.md) | [Bahasa Indonesia](README.id.md)

# RAG Chatbot API

A Retrieval-Augmented Generation (RAG) chatbot served over HTTP with FastAPI. Upload a PDF, then ask questions about it. Answers are grounded in the uploaded document and include citations. When the answer isn't in the document, the chatbot says so instead of making something up.

## Features

- Upload a PDF and have it automatically extracted, chunked, embedded, and indexed
- Ask questions through a `/chat` endpoint and get answers grounded in the document
- Every answer reports which source file it used
- A guardrail keeps the model from hallucinating: if the answer isn't in the document, it replies that the information isn't available
- Each upload replaces the previous document, so questions only touch the latest PDF
- Non-PDF uploads are rejected with a clear error message

## Tech Stack

- LLM: Groq (Llama 3.3 70B)
- Embeddings: sentence-transformers (`all-MiniLM-L6-v2`, 384-dimensional)
- Vector store: ChromaDB (persistent)
- PDF parsing: pypdf
- API: FastAPI + Uvicorn
- Config: python-dotenv

## How It Works

There are two flows.

On upload, the PDF is read into plain text, split into overlapping chunks, converted into embeddings, and stored in ChromaDB.

On chat, the incoming question is embedded and compared against the stored chunks. The most relevant chunks are pulled out, assembled into a prompt along with a guardrail instruction, and sent to the Groq LLM. The model returns an answer grounded in those chunks, along with the source files that were retrieved.

## Project Structure

### `api/`

**`main.py`** — The FastAPI application and all HTTP endpoints. Defines the request and response shapes (Pydantic models) and connects the RAG components together.

- `POST /chat` takes `{"question": "..."}` and returns `{"answer": "...", "sources": [...]}`.
- `POST /upload` accepts a PDF file, then extracts, chunks, and indexes it. Non-PDF files are rejected with a 400 error, and the knowledge base is reset first so only the newest PDF is searchable.
- `GET /` is a health check that returns `{"status": "ok"}`.

### `core/` (the RAG engine)

**`loader.py`** — Reads plain text documents (`.txt` and `.md`) and keeps track of the source filename so citations work later.

**`pdf_loader.py`** — `extract_text_from_pdf(file_path)` opens a PDF with pypdf, loops over each page, pulls out the text (skipping empty pages), and joins it into one string.

**`chunker.py`** — `chunk_text(text, chunk_size=500, overlap=50)` splits a long document into overlapping chunks. The overlap preserves context across chunk boundaries so no idea gets cut in half.

**`embedder.py`** — Converts text into vectors (embeddings) using a sentence-transformers model loaded once at import time. These 384-dimensional vectors are what make semantic search possible.

**`vectorstore.py`** — The ChromaDB wrapper, effectively the memory of the system.

- `index_chunks(chunks, source)` embeds chunks and stores them with their source metadata.
- `retrieve(query, top_k=3)` embeds the query and returns the most similar chunks, each with its source.
- `reset_collection()` wipes the collection clean, used before each upload so only the latest document is searchable.

**`generator.py`** — The generation step.

- `build_context(chunks)` stitches retrieved chunks into a single text block, tagging each with its source label.
- `answer(query, top_k=3)` retrieves context, builds a prompt with the guardrail, calls the Groq LLM, and returns the answer plus the list of sources.

### Test scripts

These are run directly for manual verification.

- **`test_key.py`** confirms the Groq API key works and the LLM responds.
- **`test_rag.py`** tests the retrieval pipeline end to end (index then retrieve).
- **`test_generator.py`** tests the full answer flow, including the guardrail on an out-of-document question.
- **`test_pdf.py`** tests `extract_text_from_pdf` on its own against a real PDF.

### Config

- **`requirements.txt`** — Pinned dependencies. Keep it updated with `pip freeze > requirements.txt`.
- **`.env`** — Holds `GROQ_API_KEY`. Never commit this.
- **`.gitignore`** — Excludes `venv/`, `.env`, `chroma_db/`, and `data/`.

## Setup (local)

    git clone https://github.com/tndsny/rag-chatbot-api.git
    cd rag-chatbot-api

    python -m venv venv
    venv\Scripts\activate

    pip install -r requirements.txt

    echo GROQ_API_KEY=your_key_here > .env

    uvicorn api.main:app --reload

Then open http://127.0.0.1:8000/docs for the interactive Swagger UI.

## Usage

1. Upload a PDF through `POST /upload`.
2. Ask a question through `POST /chat` with `{"question": "your question here"}`.
3. You get a grounded answer with citations. Questions outside the document return a polite refusal.

## Roadmap

- Rotate the Groq API key
- Observability (structured logging and request tracing)
- Evaluation (measuring answer quality)
- Multi-document mode (optional)
- Deploy to Hugging Face Spaces with Docker