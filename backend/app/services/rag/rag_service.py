"""Retrieval-augmented question answering over a user's medical documents.

Flow: embed the question and retrieve the most similar chunks from ChromaDB
(scoped to the requesting user), assemble them into a grounded prompt, and ask
the local Ollama model to answer using only that context. The answer is returned
together with its source chunks so the UI can cite where information came from.
"""

from dataclasses import dataclass

import anyio

from app.core.constants import append_disclaimer
from app.services.ai import OllamaService, get_ai_service
from app.services.rag.vector_store import RetrievedChunk, VectorStoreService, get_vector_store

# Shown when retrieval finds nothing relevant, so the model is never asked to
# answer a document question with no supporting context.
NO_CONTEXT_MESSAGE = (
    "I could not find information about that in your uploaded documents. "
    "Please make sure the relevant document has been uploaded and processed, "
    "and consider consulting a qualified healthcare professional."
)

# Maximum characters of each chunk surfaced back to the client as a citation.
_SNIPPET_LENGTH = 240


@dataclass
class RagAnswer:
    answer: str
    sources: list[RetrievedChunk]


class RagService:
    def __init__(
        self,
        vector_store: VectorStoreService | None = None,
        ai_service: OllamaService | None = None,
    ) -> None:
        self._vector_store = vector_store
        self._ai_service = ai_service

    def _get_vector_store(self) -> VectorStoreService:
        if self._vector_store is None:
            self._vector_store = get_vector_store()
        return self._vector_store

    def _get_ai_service(self) -> OllamaService:
        if self._ai_service is None:
            self._ai_service = get_ai_service()
        return self._ai_service

    async def answer_question(
        self,
        user_id: int,
        question: str,
        document_ids: list[int] | None = None,
        top_k: int | None = None,
    ) -> RagAnswer:
        # Retrieval is CPU-bound (embedding the query), so it runs in a thread.
        chunks = await anyio.to_thread.run_sync(
            self._get_vector_store().query,
            user_id,
            question,
            document_ids,
            top_k,
        )

        if not chunks:
            return RagAnswer(answer=append_disclaimer(NO_CONTEXT_MESSAGE), sources=[])

        context = self._build_context(chunks)
        answer = await self._get_ai_service().answer_with_context(question, context)
        return RagAnswer(answer=append_disclaimer(answer), sources=chunks)

    @staticmethod
    def _build_context(chunks: list[RetrievedChunk]) -> str:
        # Number each excerpt so the model can ground its answer in specific passages.
        return "\n\n".join(
            f"[Excerpt {index + 1}]\n{chunk.text}" for index, chunk in enumerate(chunks)
        )

    @staticmethod
    def snippet(text: str) -> str:
        text = text.strip()
        if len(text) <= _SNIPPET_LENGTH:
            return text
        return f"{text[:_SNIPPET_LENGTH].rstrip()}..."
