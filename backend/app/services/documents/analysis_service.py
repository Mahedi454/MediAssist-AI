"""Generate patient-friendly analyses of processed medical documents.

Builds on the text already extracted during document processing: the stored
text is sent to the local Ollama model with a structured report-analysis prompt,
and the result is cached on the document so repeat views are instant. Passing
``refresh=True`` regenerates the analysis.
"""

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.constants import append_disclaimer
from app.core.exceptions import AppException
from app.models.document import DocumentStatus, MedicalDocument
from app.models.user import User
from app.repositories.document_repository import DocumentRepository
from app.services.ai import OllamaService, get_ai_service

logger = logging.getLogger(__name__)


class ReportAnalysisService:
    def __init__(self, session: AsyncSession, ai_service: OllamaService | None = None) -> None:
        self.document_repository = DocumentRepository(session)
        self._ai_service = ai_service

    def _get_ai_service(self) -> OllamaService:
        if self._ai_service is None:
            self._ai_service = get_ai_service()
        return self._ai_service

    async def analyze(self, current_user: User, document_id: int, refresh: bool = False) -> MedicalDocument:
        document = await self.document_repository.get_by_id(document_id, current_user.id)
        if document is None:
            raise AppException("Document not found.", status_code=404, error_code="document_not_found")

        if document.status != DocumentStatus.PROCESSED.value or not document.extracted_text:
            raise AppException(
                "This document has no extracted text to analyze. "
                "Only successfully processed documents can be analyzed.",
                status_code=400,
                error_code="document_not_processed",
            )

        # Return the cached analysis unless a fresh one is explicitly requested.
        if document.analysis and not refresh:
            return document

        # Cap the input so very large reports stay within the model's context window.
        report_text = document.extracted_text[: settings.REPORT_ANALYSIS_MAX_CHARS]
        analysis = await self._get_ai_service().analyze_report(report_text)
        analysis = append_disclaimer(analysis)

        updated = await self.document_repository.set_analysis(document_id, current_user.id, analysis)
        return updated or document
