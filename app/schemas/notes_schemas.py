from datetime import datetime
from pydantic import BaseModel, Field,field_validator 
import uuid

class NoteIngestSchema(BaseModel):
    user_book_id: uuid.UUID
    content: str
    page: int | None

