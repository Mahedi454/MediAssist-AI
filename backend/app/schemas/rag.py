from pydantic import BaseModel, Field


class RagQueryRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    # Optionally restrict retrieval to specific uploaded documents. When omitted,
    # all of the current user's processed documents are searched.
    document_ids: list[int] | None = None
    top_k: int | None = Field(default=None, ge=1, le=10)


class RagSource(BaseModel):
    document_id: int
    chunk_index: int
    snippet: str


class RagAnswerResponse(BaseModel):
    answer: str
    sources: list[RagSource]
