from pydantic import BaseModel, Field,field_validator 
from datetime import datetime
import uuid

class EntryIngestSchema(BaseModel):
    """

    Attributes: 
        user_book_id: 
        content: 
        page: 
        is_private: 
        tags: 
    """
    user_book_id: uuid.UUID 
    content: str
    page: int | None = None
    is_private: bool | None = True
    tags: list[EntryTagIngestSchema] | None = Field(default_factory=list) 

    @field_validator("content")
    @classmethod
    def content_length(cls, c: str) -> str:
        """

        Args:
            c: 

        Returns:
            

        Raises:
            ValueError: 
        """
        if not c.strip():
            raise ValueError("There's no content to submit")
        return c



class EntryPublic(BaseModel):
    """

    Attributes: 
        id: 
        content: 
        page: 
        tags: 
    """
    id: uuid.UUID
    content: str
    page: int | None
    chapter: str | None
    tags: list[EntryTag] | None = Field(default_factory=list)

class EntryTag(BaseModel):
    """

    Attributes: 
        entry_id: The id for the entry
        tag_id: the id for the tag
        name: the name that will be upserted into the tags table
    """
    entry_id: uuid.UUID
    tag_id: uuid.UUID
    name: str

class EntryTagIngestSchema(BaseModel):
    """

    Attributes: 
        entry_id: The id for the entry
        name: the name that will be upserted into the tags table
    """
    entry_id: uuid.UUID
    tag_id: uuid.UUID
    name: str

class EntrySearchSchema(BaseModel):
    """

    Attributes: 
        type: The type of entry being searched for
        content: Optional field to search content
        tag_name: Optional field to searched based on tags
        date: Tuple that can search in between the indices
    """
    user_book_id: uuid.UUID
    type: str 
    content: str | None
    tag_names: list[str] | None
    dates: tuple[datetime, datetime] | None
