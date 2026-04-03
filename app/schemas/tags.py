from typing import ClassVar
from pydantic import BaseModel, ConfigDict, Field, field_validator  
import re
import uuid

class TagMetaData(BaseModel):
    icon: str
    color: str
    border_radius: int
    is_ratable: bool

class BookTagIngestSchema(BaseModel):
    book_id: uuid.UUID
    name: str
    genre: str
    rating_value: int | None
    meta_data: TagMetaData = Field(alias="metadata")

    @field_validator("name", "genre")
    @classmethod
    def clean_up_name(cls, n: str) -> str:
        clean_text = re.sub(r'[^a-zA-Z0-9\s]', '', n) 
        return clean_text.strip().title()

class PublicTag(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    rating_value: int | None
    meta_data: TagMetaData 

class TagInternal(BaseModel):
    id: uuid.UUID
    name: str
    meta_data: TagMetaData

class TagAssignment(BaseModel):
    tag: TagInternal
    rating: int | None
