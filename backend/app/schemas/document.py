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
    created_at: datetime
    updated_at: datetime


class DeleteDocumentResponse(BaseModel):
    message: str

