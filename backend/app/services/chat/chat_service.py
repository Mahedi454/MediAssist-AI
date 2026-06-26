from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import MEDICAL_DISCLAIMER
from app.core.exceptions import AppException
from app.models.chat import MessageRole
from app.models.user import User
from app.repositories.chat_repository import ChatRepository
from app.schemas.chat import ChatRequest, ConversationCreate
from app.services.ai import OllamaService, get_ai_service


class ChatService:
    def __init__(self, session: AsyncSession, ai_service: OllamaService | None = None) -> None:
        self.chat_repository = ChatRepository(session)
        self.ai_service = ai_service or get_ai_service()

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
        # Load prior turns first so the model has conversation context. The reply
        # is generated before anything is persisted, so a failed model call leaves
        # no orphan conversation or dangling user message behind.
        if payload.conversation_id is None:
            conversation = None
            history: list[tuple[str, str]] = []
        else:
            conversation = await self.get_conversation(current_user, payload.conversation_id)
            history = [(message.role, message.content) for message in conversation.messages]

        reply = await self.ai_service.generate_reply(payload.message, history)
        assistant_content = self._with_disclaimer(reply)

        if conversation is None:
            title = self._make_title(payload.message)
            conversation = await self.chat_repository.create_conversation(current_user.id, title)

        user_message = await self.chat_repository.add_message(
            conversation_id=conversation.id,
            role=MessageRole.USER.value,
            content=payload.message,
        )
        assistant_message = await self.chat_repository.add_message(
            conversation_id=conversation.id,
            role=MessageRole.ASSISTANT.value,
            content=assistant_content,
        )
        refreshed_conversation = await self.get_conversation(current_user, conversation.id)
        return refreshed_conversation, user_message, assistant_message

    @staticmethod
    def _with_disclaimer(reply: str) -> str:
        if MEDICAL_DISCLAIMER.lower() in reply.lower():
            return reply
        return f"{reply}\n\n_Disclaimer: {MEDICAL_DISCLAIMER}_"

    def _make_title(self, message: str) -> str:
        clean_message = " ".join(message.split())
        if len(clean_message) <= 60:
            return clean_message or "New healthcare conversation"
        return f"{clean_message[:57]}..."

