import re
from pydantic import BaseModel, Field,field_validator 
from datetime import datetime
import uuid

class EntryIngestSchema(BaseModel):
    user_book_id: uuid.UUID 
    content: str
    page: int | None = None
    is_private: bool | None = True
    tags: list[TagIngestSchema] | None = Field(default_factory=list) 

    @field_validator("content")
    @classmethod
    def content_length(cls, c: str) -> str:
        if not c.strip():
            raise ValueError("There's no content to submit")
        return c

class TagIngestSchema(BaseModel):
    name: str
    rating_value: int | None

    @field_validator("name")
    @classmethod
    def clean_up_name(cls, n: str) -> str:
        clean_text = re.sub(r'[^a-zA-Z0-9\s]', '', n) 
        return clean_text.strip().title()   

class EntryPublic(BaseModel):
    id: uuid.UUID
    content: str
    page: int
    tags: list[EntryTag] | None = Field(default_factory=list)

class EntryTag(BaseModel):
    entry_tag_id: uuid.UUID
    name: str

class EntryTagIngestSchema(BaseModel):
    entry_id: uuid.UUID
    tag_id: uuid.UUID
    name: str

class EntrySearchSchema(BaseModel):
    type: str | None
    content: str | None
    tag_name: str | None
    date: datetime | None
