"""Aggregate per-user activity for the dashboard home screen.

Combines counts and recent items from the chat and document repositories into a
single response so the frontend needs only one request to render the dashboard.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import DocumentStatus
from app.models.user import User
from app.repositories.chat_repository import ChatRepository
from app.repositories.document_repository import DocumentRepository
from app.schemas.chat import ConversationRead
from app.schemas.dashboard import DashboardResponse, DashboardStatistics
from app.schemas.document import DocumentRead


class DashboardService:
    def __init__(self, session: AsyncSession) -> None:
        self.chat_repository = ChatRepository(session)
        self.document_repository = DocumentRepository(session)

    async def get_overview(self, current_user: User, recent_limit: int = 5) -> DashboardResponse:
        user_id = current_user.id

        statistics = DashboardStatistics(
            total_conversations=await self.chat_repository.count_conversations(user_id),
            total_messages=await self.chat_repository.count_messages(user_id),
            total_documents=await self.document_repository.count_for_user(user_id),
            processed_documents=await self.document_repository.count_by_status(
                user_id, DocumentStatus.PROCESSED.value
            ),
            total_chunks=await self.document_repository.sum_chunks(user_id),
        )

        recent_documents = await self.document_repository.list_recent(user_id, recent_limit)
        recent_conversations = await self.chat_repository.list_recent_conversations(user_id, recent_limit)

        return DashboardResponse(
            statistics=statistics,
            recent_uploads=[DocumentRead.model_validate(document) for document in recent_documents],
            recent_chats=[ConversationRead.model_validate(conversation) for conversation in recent_conversations],
        )
