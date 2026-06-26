from typing import Annotated

from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.db.session import get_db_session
from app.models.user import User
from app.schemas.document import DeleteDocumentResponse, DocumentDetail, DocumentRead
from app.services.documents.analysis_service import ReportAnalysisService
from app.services.documents.document_service import DocumentService

router = APIRouter()


@router.post("", response_model=DocumentRead, status_code=status.HTTP_201_CREATED)
async def upload_document(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    file: Annotated[UploadFile, File()],
) -> DocumentRead:
    return await DocumentService(session).upload_document(current_user, file)


@router.get("", response_model=list[DocumentRead])
async def list_documents(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> list[DocumentRead]:
    return await DocumentService(session).list_documents(current_user)


@router.get("/{document_id}", response_model=DocumentDetail)
async def get_document(
    document_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> DocumentDetail:
    return await DocumentService(session).get_document(current_user, document_id)


@router.post("/{document_id}/analyze", response_model=DocumentDetail)
async def analyze_document(
    document_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    refresh: Annotated[bool, Query()] = False,
) -> DocumentDetail:
    return await ReportAnalysisService(session).analyze(current_user, document_id, refresh=refresh)


@router.delete("/{document_id}", response_model=DeleteDocumentResponse)
async def delete_document(
    document_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> DeleteDocumentResponse:
    await DocumentService(session).delete_document(current_user, document_id)
    return DeleteDocumentResponse(message="Document deleted successfully.")

