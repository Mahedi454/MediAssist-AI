from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import MEDICAL_DISCLAIMER
from app.core.exceptions import AppException
from app.models.chat import MessageRole
from app.models.user import User
from app.repositories.chat_repository import ChatRepository
from app.schemas.chat import ChatRequest, ConversationCreate


class ChatService:
    def __init__(self, session: AsyncSession) -> None:
        self.chat_repository = ChatRepository(session)

    async def create_conversation(self, current_user: User, payload: ConversationCreate):
        title = payload.title or "New healthcare conversation"
        return await self.chat_repository.create_conversation(current_user.id, title)

    async def list_conversations(self, current_user: User, search: str | None = None):
        return await self.chat_repository.list_conversations(current_user.id, search)

    async def get_conversation(self, current_user: User, conversation_id: int):
        conversation = await self.chat_repository.get_conversation(conversation_id, current_user.id)
        if conversation is None:
            raise AppException("Conversation not found.", status_code=404, error_code="conversation_not_found")
        return conversation

    async def delete_conversation(self, current_user: User, conversation_id: int) -> None:
        deleted = await self.chat_repository.delete_conversation(conversation_id, current_user.id)
        if not deleted:
            raise AppException("Conversation not found.", status_code=404, error_code="conversation_not_found")

    async def send_message(self, current_user: User, payload: ChatRequest):
        if payload.conversation_id is None:
            title = self._make_title(payload.message)
            conversation = await self.chat_repository.create_conversation(current_user.id, title)
        else:
            conversation = await self.get_conversation(current_user, payload.conversation_id)

        user_message = await self.chat_repository.add_message(
            conversation_id=conversation.id,
            role=MessageRole.USER.value,
            content=payload.message,
        )
        assistant_message = await self.chat_repository.add_message(
            conversation_id=conversation.id,
            role=MessageRole.ASSISTANT.value,
            content=self._build_placeholder_response(payload.message),
        )
        refreshed_conversation = await self.get_conversation(current_user, conversation.id)
        return refreshed_conversation, user_message, assistant_message

    def _build_placeholder_response(self, message: str) -> str:
        return (
            "I can help with general healthcare education. The AI model will be connected in a later step, "
            "so this temporary response has not interpreted your question clinically. "
            f"You asked: {message}\n\n"
            f"Disclaimer: {MEDICAL_DISCLAIMER}"
        )

    def _make_title(self, message: str) -> str:
        clean_message = " ".join(message.split())
        if len(clean_message) <= 60:
            return clean_message or "New healthcare conversation"
        return f"{clean_message[:57]}..."

