from typing import ClassVar
from pydantic import BaseModel, ConfigDict, field_validator  
import re
import uuid


class BookTagIngestSchema(BaseModel):
    book_id: uuid.UUID
    name: str
    rating_value: int | None

    @field_validator("name")
    @classmethod
    def clean_up_name(cls, n: str) -> str:
        clean_text = re.sub(r'[^a-zA-Z0-9\s]', '', n) 
        return clean_text.strip().title()


class EntryTagIngestSchema(BaseModel):
    entry_id: uuid.UUID
    tag_id: uuid.UUID
    name: str
    
    @field_validator("name")
    @classmethod
    def clean_up_name(cls, n: str) -> str:
        clean_text = re.sub(r'[^a-zA-Z0-9\s]', '', n) 
        return clean_text.strip().title()

class PublicTag(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    rating_value: int | None

