from datetime import datetime
from pydantic import BaseModel, Field,field_validator 
from typing import Optional, List
import uuid

class GenreIngestSchema(BaseModel):
    name: str
    
    @field_validator("name")
    @classmethod
    def clean_up_name(cls, n: str) -> str:
        return n.strip().title()
