from pydantic import BaseModel, Field, ConfigDict, model_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

class BookMetadata(BaseModel):
    categories: List[str] = Field(default_factory=list)
    description: Optional[str] = None
    image_links: Optional[Dict[str, str]] = Field(None, alias="imageLinks")
    identifiers: List[Dict[str, str]] = Field(default_factory=list, alias="industryIdentifiers")
    publisher: Optional[str] = None

class BookIngestSchema(BaseModel):
    model_config = ConfigDict(extra='allow', populate_by_name=True)

    title: str 
    isbn: str
    authors: List[str]= Field(default_factory=list) # Make sure every model has its own list
    page_count: int = Field(default=0, alias="pageCount")
    
    metadata: BookMetadata

    @model_validator(mode='before')
    @classmethod
    def wrapp_metadata(cls, data: dict):
        # Get the identifiers list
       identifiers = data.get("industryIdentifiers", [])
       found_isbn = "UNKNOWN"

        # Loop through the dictionaries and prioritize ISBN_13
        # take ISBN_10 as a backup
       for isbn_dict in identifiers:
           id_type = isbn_dict.get("type") # Get the key of the dictionary containing the type and identifier
           if id_type == "ISBN_13":
               found_isbn = isbn_dict.get("identifier")
               break # ISBN_13 is the goal, when acquired, stop looking
           elif id_type == "ISBN_10":
               found_isbn = isbn_dict.get("identifier")

      
       data["isbn"] = found_isbn

       data["metadata"] = data 

       return data

class UserBookIngest(BaseModel):
    user_id: uuid.UUID
    book_id: uuid.UUID
    current_page: Optional[int]
    reading_status: Optional[str]
    rating: Optional[float] = Field(None, ge=1, le=5)

# Data to be sent to the front end when the user wants to 
# Update their book
class DetailedBook(BaseModel):
    book_id: uuid.UUID
    title: str
    thumbnail: Optional[str]
    description: Optional[str]
    categories: Optional[List[str]] = Field()
    authors: List[str] = Field(default_factory=list)
    total_pages: Optional[int]
    added_at: Optional[datetime] = None
    rating: Optional[float] = 0

class BookSearchResult(BaseModel):
    id: uuid.UUID
    isbn: Optional[str]
    title: str
    authors: List[str] = Field(default_factory=list)

