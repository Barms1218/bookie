from pydantic import BaseModel, Field, ConfigDict, model_validator, String
from typing import Optional, Dict 
import uuid

class journal(BaseModel):
    user_id: uuid.UUID = Field(alias="userID")
    user_book_id: uuid.UUID = Field(alias="bookID")
    content: str
