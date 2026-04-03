from typing import ClassVar, TypedDict, Any
from pydantic import BaseModel, Field, ConfigDict, model_validator
from datetime import datetime
import uuid

class IndustryIdentifier(TypedDict):
    type: str
    identifier: str

class BookMetadata(BaseModel):
    categories: list[str] = Field(default_factory=list)
    description: str | None = None
    image_links: dict[str, str] | None = Field(default_factory=dict, alias="imageLinks")
    identifiers: list[dict[str, str]] = Field(default_factory=list, alias="industryIdentifiers")
    publisher: str | None = None

class BookIngestSchema(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(extra='ignore', populate_by_name=True)

    title: str 
    isbn: str
    authors: list[str]= Field(default_factory=list) # Make sure every model has its own list
    page_count: int = Field(default=0, alias="pageCount")
    
    meta_data: BookMetadata = Field(alias="metadata")

    @model_validator(mode='before')
    @classmethod
    def wrap_metadata(cls, data: dict[str, Any]):
        # Get the identifiers list
       identifiers: list[IndustryIdentifier] = data.get("industryIdentifiers", [])
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
    current_page: int | None 
    reading_status: str | None 
    rating: int | None = Field(None, ge=1, le=5)

# Data to be sent to the front end when the user wants to 
# Update their book
class DetailedBook(BaseModel):
    book_id: uuid.UUID
    title: str
    thumbnail: str | None 
    description: str | None 
    categories: list[str] | None = Field(default_factory=list)
    authors: list[str] = Field(default_factory=list)
    total_pages: int | None 
    added_at: datetime | None = None
    rating: int | None = 0

class BookSearchResult(BaseModel):
    id: uuid.UUID
    isbn: str | None 
    title: str
    authors: list[str] = Field(default_factory=list)

