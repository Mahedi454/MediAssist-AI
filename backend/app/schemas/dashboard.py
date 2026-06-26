from pydantic import BaseModel

from app.schemas.chat import ConversationRead
from app.schemas.document import DocumentRead


class DashboardStatistics(BaseModel):
    total_conversations: int
    total_messages: int
    total_documents: int
    processed_documents: int
    total_chunks: int


class DashboardResponse(BaseModel):
    statistics: DashboardStatistics
    recent_uploads: list[DocumentRead]
    recent_chats: list[ConversationRead]
