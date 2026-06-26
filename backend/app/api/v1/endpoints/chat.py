from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.db.session import get_db_session
from app.models.user import User
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ConversationCreate,
    ConversationDetail,
    ConversationRead,
    DeleteConversationResponse,
)
from app.services.chat.chat_service import ChatService

router = APIRouter()


@router.post("/conversations", response_model=ConversationRead, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    payload: ConversationCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ConversationRead:
    return await ChatService(session).create_conversation(current_user, payload)


@router.get("/conversations", response_model=list[ConversationRead])
async def list_conversations(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    search: Annotated[str | None, Query(max_length=255)] = None,
) -> list[ConversationRead]:
    return await ChatService(session).list_conversations(current_user, search)


@router.get("/conversations/{conversation_id}", response_model=ConversationDetail)
async def get_conversation(
    conversation_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ConversationDetail:
    return await ChatService(session).get_conversation(current_user, conversation_id)


@router.delete("/conversations/{conversation_id}", response_model=DeleteConversationResponse)
async def delete_conversation(
    conversation_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> DeleteConversationResponse:
    await ChatService(session).delete_conversation(current_user, conversation_id)
    return DeleteConversationResponse(message="Conversation deleted successfully.")


@router.post("/messages", response_model=ChatResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    payload: ChatRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ChatResponse:
    conversation, user_message, assistant_message = await ChatService(session).send_message(current_user, payload)
    return ChatResponse(
        conversation=conversation,
        user_message=user_message,
        assistant_message=assistant_message,
    )

