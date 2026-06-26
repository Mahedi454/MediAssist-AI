from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import MedicalDocument


class DocumentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        *,
        user_id: int,
        original_filename: str,
        stored_filename: str,
        storage_path: str,
        content_type: str,
        file_extension: str,
        size_bytes: int,
    ) -> MedicalDocument:
        document = MedicalDocument(
            user_id=user_id,
            original_filename=original_filename,
            stored_filename=stored_filename,
            storage_path=storage_path,
            content_type=content_type,
            file_extension=file_extension,
            size_bytes=size_bytes,
        )
        self.session.add(document)
        await self.session.commit()
        await self.session.refresh(document)
        return document

    async def set_processing_result(
        self,
        document_id: int,
        user_id: int,
        *,
        status: str,
        extracted_text: str | None = None,
        chunk_count: int = 0,
        error: str | None = None,
    ) -> MedicalDocument | None:
        document = await self.get_by_id(document_id, user_id)
        if document is None:
            return None
        document.status = status
        document.extracted_text = extracted_text
        document.chunk_count = chunk_count
        document.error = error
        await self.session.commit()
        await self.session.refresh(document)
        return document

    async def set_analysis(self, document_id: int, user_id: int, analysis: str) -> MedicalDocument | None:
        document = await self.get_by_id(document_id, user_id)
        if document is None:
            return None
        document.analysis = analysis
        await self.session.commit()
        await self.session.refresh(document)
        return document

    async def get_by_id(self, document_id: int, user_id: int) -> MedicalDocument | None:
        result = await self.session.execute(
            select(MedicalDocument).where(MedicalDocument.id == document_id, MedicalDocument.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def list_for_user(self, user_id: int) -> list[MedicalDocument]:
        result = await self.session.execute(
            select(MedicalDocument)
            .where(MedicalDocument.user_id == user_id)
            .order_by(MedicalDocument.created_at.desc())
        )
        return list(result.scalars().all())

    async def delete(self, document_id: int, user_id: int) -> bool:
        result = await self.session.execute(
            delete(MedicalDocument).where(MedicalDocument.id == document_id, MedicalDocument.user_id == user_id)
        )
        await self.session.commit()
        return bool(result.rowcount)

