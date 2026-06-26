from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user
from app.models.user import User
from app.schemas.rag import RagAnswerResponse, RagQueryRequest, RagSource
from app.services.rag.rag_service import RagService

router = APIRouter()


@router.post("/ask", response_model=RagAnswerResponse)
async def ask_documents(
    payload: RagQueryRequest,
    current_user: Annotated[User, Depends(get_current_user)],
) -> RagAnswerResponse:
    """Answer a question using only the current user's uploaded documents."""
    service = RagService()
    result = await service.answer_question(
        user_id=current_user.id,
        question=payload.question,
        document_ids=payload.document_ids,
        top_k=payload.top_k,
    )
    return RagAnswerResponse(
        answer=result.answer,
        sources=[
            RagSource(
                document_id=chunk.document_id,
                chunk_index=chunk.chunk_index,
                snippet=RagService.snippet(chunk.text),
            )
            for chunk in result.sources
        ],
    )
