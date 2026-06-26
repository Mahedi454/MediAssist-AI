"""Split extracted document text into overlapping chunks for embedding.

A recursive splitter keeps related sentences together by preferring natural
boundaries (paragraphs, then lines, then sentences) before falling back to a
hard character cut. Overlap preserves context across chunk boundaries so a fact
that straddles two chunks is still retrievable.
"""

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import settings

_splitter = RecursiveCharacterTextSplitter(
    chunk_size=settings.CHUNK_SIZE,
    chunk_overlap=settings.CHUNK_OVERLAP,
    separators=["\n\n", "\n", ". ", " ", ""],
)


def chunk_text(text: str) -> list[str]:
    """Return non-empty, trimmed chunks for ``text`` (empty list if no content)."""
    if not text or not text.strip():
        return []
    return [chunk.strip() for chunk in _splitter.split_text(text) if chunk.strip()]
