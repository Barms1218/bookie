from pydantic import BaseModel, Field
from typing import Optional, List

class User(BaseModel):
    title: str
    isbn_10: str
    isbn_13: str = Field(alias="isbn")
    authors: List[str]
    page_count: int
    
