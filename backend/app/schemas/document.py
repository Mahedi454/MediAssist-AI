from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    original_filename: str
    content_type: str
    file_extension: str
    size_bytes: int
    status: str
    chunk_count: int = 0
    error: str | None = None
    created_at: datetime
    updated_at: datetime


class DocumentDetail(DocumentRead):
    extracted_text: str | None = None


class DeleteDocumentResponse(BaseModel):
    message: str

