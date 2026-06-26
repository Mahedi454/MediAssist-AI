import logging
from pathlib import Path
from uuid import uuid4

import anyio
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import AppException
from app.models.document import DocumentStatus, MedicalDocument
from app.models.user import User
from app.repositories.document_repository import DocumentRepository
from app.services.documents.text_extractor import TextExtractor
from app.services.rag import chunk_text
from app.services.rag.vector_store import VectorStoreService, get_vector_store

logger = logging.getLogger(__name__)


class DocumentService:
    allowed_extensions = {".pdf", ".docx", ".txt", ".png", ".jpg", ".jpeg"}

    def __init__(
        self,
        session: AsyncSession,
        text_extractor: TextExtractor | None = None,
        vector_store: VectorStoreService | None = None,
    ) -> None:
        self.document_repository = DocumentRepository(session)
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.text_extractor = text_extractor or TextExtractor()
        # Loading the embedding model is expensive, so the vector store is
        # resolved lazily (only when a document is ingested or deleted).
        self._vector_store = vector_store

    def _get_vector_store(self) -> VectorStoreService:
        if self._vector_store is None:
            self._vector_store = get_vector_store()
        return self._vector_store

    async def upload_document(self, current_user: User, file: UploadFile):
        original_filename = Path(file.filename or "").name
        extension = Path(original_filename).suffix.lower()

        if not original_filename or extension not in self.allowed_extensions:
            raise AppException(
                "Unsupported file type. Upload PDF, DOCX, TXT, PNG, JPG, or JPEG files.",
                status_code=400,
                error_code="unsupported_file_type",
            )

        content = await file.read()
        size_bytes = len(content)
        max_size_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        if size_bytes == 0:
            raise AppException("Uploaded file is empty.", status_code=400, error_code="empty_file")
        if size_bytes > max_size_bytes:
            raise AppException(
                f"Uploaded file exceeds the {settings.MAX_UPLOAD_SIZE_MB} MB limit.",
                status_code=413,
                error_code="file_too_large",
            )

        user_upload_dir = self.upload_dir / str(current_user.id)
        user_upload_dir.mkdir(parents=True, exist_ok=True)

        stored_filename = f"{uuid4().hex}{extension}"
        storage_path = user_upload_dir / stored_filename
        storage_path.write_bytes(content)

        document = await self.document_repository.create(
            user_id=current_user.id,
            original_filename=original_filename,
            stored_filename=stored_filename,
            storage_path=str(storage_path),
            content_type=file.content_type or "application/octet-stream",
            file_extension=extension,
            size_bytes=size_bytes,
        )

        return await self._process_document(document)

    async def _process_document(self, document: MedicalDocument) -> MedicalDocument:
        """Extract text from a stored document and record the outcome.

        Extraction is CPU-bound (parsing/OCR), so it runs in a worker thread to
        keep the event loop responsive. A failure marks the document as failed
        with a short error message instead of breaking the upload request.
        """
        try:
            extracted_text = await anyio.to_thread.run_sync(
                self.text_extractor.extract,
                Path(document.storage_path),
                document.file_extension,
            )
            chunks = chunk_text(extracted_text)
            chunk_count = 0
            if chunks:
                chunk_count = await anyio.to_thread.run_sync(
                    self._get_vector_store().add_document,
                    document.user_id,
                    document.id,
                    chunks,
                )
        except Exception as exc:  # noqa: BLE001 - any parse/OCR/embedding error marks the doc failed
            logger.exception("Document processing failed for document %s", document.id)
            updated = await self.document_repository.set_processing_result(
                document.id,
                document.user_id,
                status=DocumentStatus.FAILED.value,
                error=str(exc)[:500],
            )
            return updated or document

        updated = await self.document_repository.set_processing_result(
            document.id,
            document.user_id,
            status=DocumentStatus.PROCESSED.value,
            extracted_text=extracted_text or None,
            chunk_count=chunk_count,
        )
        return updated or document

    async def list_documents(self, current_user: User):
        return await self.document_repository.list_for_user(current_user.id)

    async def get_document(self, current_user: User, document_id: int):
        document = await self.document_repository.get_by_id(document_id, current_user.id)
        if document is None:
            raise AppException("Document not found.", status_code=404, error_code="document_not_found")
        return document

    async def delete_document(self, current_user: User, document_id: int) -> None:
        document = await self.get_document(current_user, document_id)
        deleted = await self.document_repository.delete(document_id, current_user.id)
        if not deleted:
            raise AppException("Document not found.", status_code=404, error_code="document_not_found")

        storage_path = Path(document.storage_path)
        if storage_path.exists() and storage_path.is_file():
            storage_path.unlink()

        # Remove the document's chunks from the vector store so deleted documents
        # can never surface in future retrieval results.
        await anyio.to_thread.run_sync(
            self._get_vector_store().delete_document,
            current_user.id,
            document_id,
        )

