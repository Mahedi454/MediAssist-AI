# Architecture Notes

## High-Level Modules

- Authentication: registration, login, logout, JWT validation, and profile access.
- General chat: healthcare education chat with a mandatory medical disclaimer.
- Document upload: secure upload and metadata tracking for PDF, DOCX, TXT, PNG, and JPG.
- Document processing: text extraction, OCR, chunking, embeddings, and vector storage.
- RAG: retrieve uploaded document chunks and answer only from cited document context.
- Admin: user management, uploaded document visibility, usage monitoring, and logs.

## Safety Rule

AI responses must provide educational information only and must include a disclaimer that they are not a substitute for professional medical advice.

