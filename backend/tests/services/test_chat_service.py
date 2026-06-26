from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.core.constants import EMERGENCY_NOTICE, MEDICAL_DISCLAIMER
from app.core.exceptions import AppException
from app.schemas.chat import ChatRequest
from app.services.chat.chat_service import ChatService


def _make_service(ai_reply: str = "Here is some educational information.") -> tuple[ChatService, AsyncMock]:
    ai = AsyncMock()
    ai.generate_reply = AsyncMock(return_value=ai_reply)
    # session is only used to build the repository, which we replace with a mock.
    service = ChatService(session=None, ai_service=ai)
    service.chat_repository = AsyncMock()
    return service, ai


async def test_send_message_creates_conversation_and_appends_disclaimer() -> None:
    service, ai = _make_service("Diabetes affects blood sugar regulation.")
    repo = service.chat_repository
    conversation = SimpleNamespace(id=1, messages=[])
    repo.create_conversation = AsyncMock(return_value=conversation)
    repo.add_message = AsyncMock(side_effect=[SimpleNamespace(id=1), SimpleNamespace(id=2)])
    repo.get_conversation = AsyncMock(return_value=SimpleNamespace(id=1, messages=[]))

    user = SimpleNamespace(id=99)
    _, _, _ = await service.send_message(user, ChatRequest(message="What is diabetes?"))

    ai.generate_reply.assert_awaited_once()
    repo.create_conversation.assert_awaited_once()
    assistant_content = repo.add_message.await_args_list[1].kwargs["content"]
    assert MEDICAL_DISCLAIMER in assistant_content


async def test_send_message_prepends_emergency_notice() -> None:
    service, _ = _make_service("Chest pain can have many causes.")
    repo = service.chat_repository
    repo.create_conversation = AsyncMock(return_value=SimpleNamespace(id=1, messages=[]))
    repo.add_message = AsyncMock(side_effect=[SimpleNamespace(id=1), SimpleNamespace(id=2)])
    repo.get_conversation = AsyncMock(return_value=SimpleNamespace(id=1, messages=[]))

    await service.send_message(SimpleNamespace(id=1), ChatRequest(message="I have severe chest pain"))

    assistant_content = repo.add_message.await_args_list[1].kwargs["content"]
    assert assistant_content.startswith(EMERGENCY_NOTICE)


async def test_send_message_failure_persists_nothing() -> None:
    service, ai = _make_service()
    ai.generate_reply = AsyncMock(
        side_effect=AppException("down", status_code=503, error_code="ai_service_unavailable")
    )
    repo = service.chat_repository
    repo.get_conversation = AsyncMock(return_value=SimpleNamespace(id=5, messages=[]))

    with pytest.raises(AppException):
        await service.send_message(SimpleNamespace(id=1), ChatRequest(message="hi", conversation_id=5))

    # The reply is generated before persistence, so a failure stores nothing.
    repo.add_message.assert_not_called()
    repo.create_conversation.assert_not_called()


def test_make_title_truncates_long_messages() -> None:
    service, _ = _make_service()
    assert service._make_title("What is diabetes?") == "What is diabetes?"
    long_title = service._make_title("a" * 100)
    assert len(long_title) <= 60
    assert long_title.endswith("...")
