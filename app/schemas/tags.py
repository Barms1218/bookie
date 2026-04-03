from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field,field_validator, model_validator 
import re
import uuid

class TagMetaData(BaseModel):
    icon: str
    color: str
    is_ratable: bool

class TagIngestSchema(BaseModel):
    book_id: uuid.UUID
    name: str
    genre: str
    rating: float | None
    meta_data: TagMetaData = Field(alias="metaData")

    @field_validator("name", "genre")
    @classmethod
    def clean_up_name(cls, n: str) -> str:
        clean_text = re.sub(r'[^a-zA-Z0-9]', '', n) 
        return clean_text.strip().title()

class PublicTag(BaseModel):
    id: uuid.UUID
    name: str
    rating_value: int | None
    meta_data: dict[str, Any]

class TagInternal(BaseModel):
    id: uuid.UUID
    name: str
    meta_data: dict[str, Any]

class TagAssignment(BaseModel):
    tag: TagInternal
    rating: int | None
