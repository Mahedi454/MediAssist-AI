from datetime import datetime, timezone

from sqlalchemy import delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.chat import ChatMessage, Conversation


class ChatRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_conversation(self, user_id: int, title: str) -> Conversation:
        conversation = Conversation(user_id=user_id, title=title)
        self.session.add(conversation)
        await self.session.commit()
        await self.session.refresh(conversation)
        return conversation

    async def get_conversation(self, conversation_id: int, user_id: int) -> Conversation | None:
        result = await self.session.execute(
            select(Conversation)
            .where(Conversation.id == conversation_id, Conversation.user_id == user_id)
            .options(selectinload(Conversation.messages))
        )
        return result.scalar_one_or_none()

    async def list_conversations(self, user_id: int, search: str | None = None) -> list[Conversation]:
        statement = select(Conversation).where(Conversation.user_id == user_id)
        if search:
            search_term = f"%{search.lower()}%"
            statement = (
                statement.outerjoin(ChatMessage)
                .where(
                    or_(
                        Conversation.title.ilike(search_term),
                        ChatMessage.content.ilike(search_term),
                    )
                )
                .distinct()
            )
        statement = statement.order_by(Conversation.updated_at.desc())
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def add_message(self, conversation_id: int, role: str, content: str) -> ChatMessage:
        message = ChatMessage(conversation_id=conversation_id, role=role, content=content)
        self.session.add(message)
        conversation = await self.session.get(Conversation, conversation_id)
        if conversation is not None:
            conversation.updated_at = datetime.now(timezone.utc)
        await self.session.commit()
        await self.session.refresh(message)
        return message

    async def delete_conversation(self, conversation_id: int, user_id: int) -> bool:
        result = await self.session.execute(
            delete(Conversation).where(Conversation.id == conversation_id, Conversation.user_id == user_id)
        )
        await self.session.commit()
        return bool(result.rowcount)

    async def count_conversations(self, user_id: int) -> int:
        result = await self.session.execute(
            select(func.count()).select_from(Conversation).where(Conversation.user_id == user_id)
        )
        return int(result.scalar_one())

    async def count_messages(self, user_id: int) -> int:
        result = await self.session.execute(
            select(func.count())
            .select_from(ChatMessage)
            .join(Conversation, ChatMessage.conversation_id == Conversation.id)
            .where(Conversation.user_id == user_id)
        )
        return int(result.scalar_one())

    async def list_recent_conversations(self, user_id: int, limit: int) -> list[Conversation]:
        result = await self.session.execute(
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
