from typing import ClassVar, TypedDict, Any
from pydantic import BaseModel, Field, ConfigDict, model_validator, field_validator
import re
import uuid

allowed_types: list[str] = [
        "Genre",
        "Character",
        "Concept"
        ]

class TagIngestSchema(BaseModel):
    name: str
    type: str

    @field_validator('name')
    @classmethod
    def clean_name(cls, n: str) -> str:
        if "&" in n:
            n = str.replace(n, "&", "and")
        cleaned_name = n.strip().title()

        clean_string: str = re.sub(r'[^a-zA-Z0-9\s-]', '', cleaned_name)

        if not clean_string:
            raise ValueError("Tag name contains no valid characters")
        
        return clean_string
    
    @field_validator('type')
    @classmethod
    def verify_type(cls, t: str) -> str:
        if t not in allowed_types:
            raise ValueError("That is not a valid type of tag.")

        return t

class PublicTag(BaseModel):
    id: uuid.UUID
    name: str
    type: str
