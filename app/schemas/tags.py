from datetime import datetime
from pydantic import BaseModel, Field,field_validator, model_validator 
from typing import Optional, List
import uuid

from sqlalchemy.orm import attribute_keyed_dict

class TagMetaData(BaseModel):
    icon: str
    color: str
    is_ratable: bool

class TagIngestSchema(BaseModel):
    name: str
    genre: str
    rating: Optional[float]
    meta_data: TagMetaData = Field(alias="metaData")

    @field_validator("name", "genre")
    @classmethod
    def clean_up_name(cls, n: str) -> str:
        return n.strip().title()

class PublicTag(BaseModel):
    id: uuid.UUID
    book_id: uuid.UUID
    name: str
