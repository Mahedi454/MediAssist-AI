from unittest.mock import AsyncMock, MagicMock

from app.services.rag.rag_service import NO_CONTEXT_MESSAGE, RagService
from app.services.rag.vector_store import RetrievedChunk


async def test_answer_question_without_matches_returns_fallback() -> None:
    vector_store = MagicMock()
    vector_store.query = MagicMock(return_value=[])
    ai = AsyncMock()

    service = RagService(vector_store=vector_store, ai_service=ai)
    result = await service.answer_question(user_id=1, question="What medication do I take?")

    assert NO_CONTEXT_MESSAGE in result.answer
    assert "Disclaimer" in result.answer
    assert result.sources == []
    # The model must not be asked to answer when there is no supporting context.
    ai.answer_with_context.assert_not_called()


async def test_answer_question_uses_retrieved_context() -> None:
    chunk = RetrievedChunk(text="Prescription: Metformin 500mg", document_id=7, chunk_index=0, distance=0.12)
    vector_store = MagicMock()
    vector_store.query = MagicMock(return_value=[chunk])
    ai = AsyncMock()
    ai.answer_with_context = AsyncMock(return_value="You are prescribed Metformin.")

    service = RagService(vector_store=vector_store, ai_service=ai)
    result = await service.answer_question(user_id=1, question="What medication do I take?")

    ai.answer_with_context.assert_awaited_once()
    _, context = ai.answer_with_context.await_args.args
    assert "Metformin 500mg" in context
    assert result.sources == [chunk]
    assert "Disclaimer" in result.answer


def test_snippet_truncates_long_text() -> None:
    assert RagService.snippet("short") == "short"
    long_snippet = RagService.snippet("a" * 500)
    assert long_snippet.endswith("...")
    assert len(long_snippet) <= 244  # 240 chars + ellipsis
