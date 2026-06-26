# AI Healthcare Chatbot

Full-stack healthcare assistant with authentication, general medical chat, medical document upload, OCR, document analysis, and RAG-based answers.

This project is being built step by step.

## Planned Stack

- Frontend: Flutter
- Backend: Python, FastAPI
- AI/RAG: LangChain, Ollama with Gemma 3 by default, switchable later to Llama 3 or Qwen through Ollama
- Vector database: ChromaDB
- Database: PostgreSQL
- File storage: Local storage for development
- Document processing: PyMuPDF, pdfplumber, Tesseract OCR

## Current Progress

- Step 1: Project folder structure
- Step 2: FastAPI backend foundation
- Step 3: Authentication API
- Step 4: Chat API
- Step 5: Medical document upload API
- Step 6: Ollama-powered chat (LangChain + Gemma 3)
- Step 7: Medical chat with emergency safety notices
- Step 8: Document text extraction and OCR (PDF, DOCX, TXT, images)
- Step 9-10: Chunking, embeddings (Sentence Transformers), and ChromaDB storage
- Step 11-13: RAG question answering over uploaded documents with citations
- Step 14: Patient-friendly medical report analysis
- Step 15: Dashboard overview (statistics, recent uploads and chats)
- Step 18: Docker Compose stack (backend, PostgreSQL, Ollama)

## Run With Docker (recommended)

Runs the whole stack — FastAPI backend, PostgreSQL, and Ollama — with one command.

```bash
docker compose up -d --build
docker compose exec ollama ollama pull gemma3   # one-time model download
```

Then open `http://localhost:8000/docs`. Database tables are created automatically
on startup, and uploads, the vector store, and the embedding model are persisted
in Docker volumes.

## Backend Quick Start (local)

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

This requires a local PostgreSQL and a running Ollama (`ollama pull gemma3`).

Then open:

- `http://localhost:8000/docs`
- `http://localhost:8000/api/v1/health`

### Optional: OCR for scanned documents and images

Text PDFs, DOCX, and TXT files work out of the box. To extract text from
scanned PDFs and images (PNG/JPG), install Tesseract OCR and point the backend
at it:

1. Install Tesseract (Windows: <https://github.com/UB-Mannheim/tesseract/wiki>).
2. Set `TESSERACT_CMD` in `.env` to the binary path, for example
   `TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe`.

Without Tesseract, uploads of scanned files are still accepted but marked with a
`failed` processing status.
