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

## Backend Quick Start

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Then open:

- `http://localhost:8000/docs`
- `http://localhost:8000/api/v1/health`
