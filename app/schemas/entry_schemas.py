import re
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
    tags: list[TagIngestSchema] | None = Field(default_factory=list) 

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

class TagIngestSchema(BaseModel):
    """

    Attributes: 
        name: 
        rating_value: 
    """
    name: str
    rating_value: int | None

    @field_validator("name")
    @classmethod
    def clean_up_name(cls, n: str) -> str:
        """

        Args:
            n: 

        Returns:
            
        """
        clean_text = re.sub(r'[^a-zA-Z0-9\s]', '', n) 
        return clean_text.strip().title()   

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
    page: int
    tags: list[EntryTag] | None = Field(default_factory=list)

class EntryTag(BaseModel):
    """

    Attributes: 
        entry_tag_id: The id of the entry that  tag is being added to
        name: The name of the tag
    """
    entry_tag_id: uuid.UUID
    name: str

class EntryTagIngestSchema(BaseModel):
    """

    Attributes: 
        entry_id: The id for the entry
        tag_id: the id for the tag
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
    type: str | None
    content: str | None
    tag_names: list[str] | None
    dates: tuple[datetime, datetime] | None
