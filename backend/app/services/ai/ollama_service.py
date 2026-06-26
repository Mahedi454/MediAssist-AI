"""LangChain-based client for the local Ollama LLM.

The model runs entirely offline through Ollama, so no paid API is involved.
The active model (Gemma 3 by default) can be swapped to Llama 3 or Qwen by
changing ``OLLAMA_MODEL`` in the environment.
"""

import logging

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_ollama import ChatOllama

from app.core.config import settings
from app.core.exceptions import AppException
from app.services.ai.prompts import RAG_SYSTEM_PROMPT, RAG_USER_TEMPLATE, SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class OllamaService:
    """Wraps a local Ollama model exposed through LangChain's ``ChatOllama``."""

    def __init__(self) -> None:
        self._client = ChatOllama(
            base_url=settings.OLLAMA_BASE_URL,
            model=settings.OLLAMA_MODEL,
            temperature=settings.OLLAMA_TEMPERATURE,
        )

    async def generate_reply(self, message: str, history: list[tuple[str, str]] | None = None) -> str:
        """Generate an assistant reply for ``message`` given prior conversation turns.

        ``history`` is an ordered list of ``(role, content)`` tuples from earlier in
        the conversation; only user and assistant turns are forwarded to the model.
        """
        messages = self._build_messages(message, history or [])
        return await self._invoke(messages)

    async def answer_with_context(self, question: str, context: str) -> str:
        """Answer ``question`` grounded strictly in the supplied document ``context``.

        Uses a retrieval-augmented system prompt that forbids using outside
        knowledge, so the model stays within the user's own documents.
        """
        messages: list[BaseMessage] = [
            SystemMessage(content=RAG_SYSTEM_PROMPT),
            HumanMessage(content=RAG_USER_TEMPLATE.format(context=context, question=question)),
        ]
        return await self._invoke(messages)

    async def _invoke(self, messages: list[BaseMessage]) -> str:
        try:
            response = await self._client.ainvoke(messages)
        except Exception as exc:  # noqa: BLE001 - surface any transport/runtime error uniformly
            logger.exception("Ollama request failed")
            raise AppException(
                "The AI assistant is temporarily unavailable. "
                "Please make sure Ollama is running and try again.",
                status_code=503,
                error_code="ai_service_unavailable",
            ) from exc

        text = self._extract_text(response.content)
        if not text:
            raise AppException(
                "The AI assistant returned an empty response. Please try again.",
                status_code=502,
                error_code="ai_empty_response",
            )
        return text

    def _build_messages(self, message: str, history: list[tuple[str, str]]) -> list[BaseMessage]:
        messages: list[BaseMessage] = [SystemMessage(content=SYSTEM_PROMPT)]
        for role, content in history:
            if role == "user":
                messages.append(HumanMessage(content=content))
            elif role == "assistant":
                messages.append(AIMessage(content=content))
        messages.append(HumanMessage(content=message))
        return messages

    @staticmethod
    def _extract_text(content: str | list) -> str:
        # ChatOllama usually returns a plain string, but multimodal models may
        # return a list of content blocks; normalise both to a single string.
        if isinstance(content, list):
            content = "".join(part if isinstance(part, str) else str(part) for part in content)
        return content.strip()


_ai_service: OllamaService | None = None


def get_ai_service() -> OllamaService:
    """Return a lazily-initialised singleton ``OllamaService``.

    The underlying ``ChatOllama`` client is reusable across requests, so a single
    shared instance avoids re-creating it on every chat message.
    """
    global _ai_service
    if _ai_service is None:
        _ai_service = OllamaService()
    return _ai_service
