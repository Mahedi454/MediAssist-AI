"""Persistent ChromaDB vector store for document chunks.

Embeddings are produced locally with a free Sentence-Transformers model
(``all-MiniLM-L6-v2`` by default), so no paid API or network service is needed
after the model is first downloaded. All chunks live in a single collection and
are tagged with ``user_id``/``document_id`` so every query is scoped to the
requesting user and, optionally, to specific documents.

The client and embedding model are loaded once and reused. Methods are
synchronous and CPU-bound; async callers should run them in a worker thread.
"""

import logging

import chromadb
from chromadb.utils import embedding_functions

from app.core.config import settings

logger = logging.getLogger(__name__)


class RetrievedChunk:
    """A single retrieved chunk with its source metadata and distance."""

    def __init__(self, text: str, document_id: int, chunk_index: int, distance: float | None) -> None:
        self.text = text
        self.document_id = document_id
        self.chunk_index = chunk_index
        self.distance = distance


class VectorStoreService:
    def __init__(self) -> None:
        self._client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
        self._embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=settings.EMBEDDING_MODEL
        )
        self._collection = self._client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION,
            embedding_function=self._embedding_function,
            metadata={"hnsw:space": "cosine"},
        )

    def add_document(self, user_id: int, document_id: int, chunks: list[str]) -> int:
        """Embed and store ``chunks`` for a document. Returns the number stored."""
        if not chunks:
            return 0
        # Replace any existing vectors for this document first so re-processing
        # never leaves stale chunks behind.
        self.delete_document(user_id, document_id)
        ids = [f"{document_id}-{index}" for index in range(len(chunks))]
        metadatas = [
            {"user_id": user_id, "document_id": document_id, "chunk_index": index}
            for index in range(len(chunks))
        ]
        self._collection.add(ids=ids, documents=chunks, metadatas=metadatas)
        return len(chunks)

    def delete_document(self, user_id: int, document_id: int) -> None:
        self._collection.delete(
            where={"$and": [{"user_id": user_id}, {"document_id": document_id}]}
        )

    def query(
        self,
        user_id: int,
        question: str,
        document_ids: list[int] | None = None,
        top_k: int | None = None,
    ) -> list[RetrievedChunk]:
        """Return the most relevant chunks for ``question`` within the user's documents."""
        conditions: list[dict] = [{"user_id": user_id}]
        if document_ids:
            conditions.append({"document_id": {"$in": document_ids}})
        where = conditions[0] if len(conditions) == 1 else {"$and": conditions}

        result = self._collection.query(
            query_texts=[question],
            n_results=top_k or settings.RAG_TOP_K,
            where=where,
        )

        documents = (result.get("documents") or [[]])[0]
        metadatas = (result.get("metadatas") or [[]])[0]
        distances = (result.get("distances") or [[]])[0]

        chunks: list[RetrievedChunk] = []
        for index, text in enumerate(documents):
            metadata = metadatas[index] if index < len(metadatas) else {}
            distance = distances[index] if index < len(distances) else None
            chunks.append(
                RetrievedChunk(
                    text=text,
                    document_id=int(metadata.get("document_id", 0)),
                    chunk_index=int(metadata.get("chunk_index", 0)),
                    distance=distance,
                )
            )
        return chunks


_vector_store: VectorStoreService | None = None


def get_vector_store() -> VectorStoreService:
    """Return a lazily-initialised singleton ``VectorStoreService``.

    Initialisation loads the embedding model (and downloads it on first use),
    so it is deferred until a document actually needs to be embedded or queried.
    """
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStoreService()
    return _vector_store
