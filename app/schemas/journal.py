from pydantic import BaseModel, Field, Integer, field_validator, model_validator, String
from typing import Optional, Dict
import uuid

class JournalIngestSchema(BaseModel):
    user_id: uuid.UUID = Field(alias="userID")
    user_book_id: uuid.UUID = Field(alias="bookID")
    content: str
    quote: Optional[QuoteIngestSchema]

    @field_validator("content")
    @classmethod
    def content_length(cls, c: str) -> str:
        if not c.strip():
            raise ValueError("There's no content to submit")
        return c

class QuoteIngestSchema(BaseModel):
    user_id: uuid.UUID = Field(alias="userID")
    user_book: uuid.UUID = Field(alias="bookID")
    character: Optional[str]
    page_number: Optional[int] = Field(alias="pageNumber")
