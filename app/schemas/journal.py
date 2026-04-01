from datetime import datetime
from pydantic import BaseModel, Field, Integer, field_validator, model_validator, String
from typing import Optional, Dict, List
import uuid

class JournalIngestSchema(BaseModel):
    user_id: uuid.UUID = Field(alias="userID")
    user_book_id: uuid.UUID = Field(alias="bookID")
    content: str
    page: Optional[int] = None


    @field_validator("content")
    @classmethod
    def content_length(cls, c: str) -> str:
        if not c.strip():
            raise ValueError("There's no content to submit")
        return c

class JournalPublic(BaseModel):
    id: uuid.UUID
    book_title: str
    content: str
    date_made: datetime
    vibe: Optional[str]

class QuoteIngestSchema(BaseModel):
    user_id: uuid.UUID = Field(alias="userID")
    user_book_id: uuid.UUID = Field(alias="bookID")
    characters: Optional[List[str]] = Field(default_factory=list)
    content: str
    page_number: Optional[int] = Field(alias="pageNumber")

class QuotePublic(BaseModel):
    id: uuid.UUID = Field(alias="quoteID")
    book_title: Optional[str] = Field(alias="bookTitle", default=None)
    characters: Optional[List[str]] = Field(default_factory=list)
    content: str
    page_number: Optional[int] = Field(default=None)

    @field_validator("book_title")
    @classmethod
    def book_title_not_empty(cls, t: str) -> str:
        if not t.strip():
            raise ValueError("No book title found for this quote")
        return t
