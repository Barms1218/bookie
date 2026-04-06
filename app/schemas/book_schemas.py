from typing import ClassVar, TypedDict, Any
from pydantic import BaseModel, Field, ConfigDict, model_validator, field_validator
from datetime import datetime
import uuid
import re

from app.schemas.entry_schemas import EntryPublic
from app.schemas.tags import PublicTag

class IndustryIdentifier(TypedDict):
    type: str
    identifier: str

class BookMetadata(BaseModel):
    categories: list[str] = Field(default_factory=list)
    small_thumbnail: str | None = None
    thumbnail: str | None = None
    identifiers: list[dict[str, str]] = Field(default_factory=list, alias="industryIdentifiers")
    publisher: str | None = None

class BookIngestSchema(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(extra='ignore', populate_by_name=True)

    title: str 
    isbn: str | None = None
    authors: list[str]= Field(default_factory=list) # Make sure every model has its own list
    page_count: int = Field(default=0, alias="pageCount")
    description: str | None = None 
    
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

       #2. Handle Image Links safely
       # Note: Google Books usually provides a dict called 'imageLinks', 
       # not a list called 'image_links'. Adjust based on your actual source!
       image_links = data.get("imageLinks", {}) 
        
       # We put these inside a new dict specifically for the Metadata model
       metadata_payload = {
            "categories": data.get("categories", []),
            "publisher": data.get("publisher"),
            "small_thumbnail": image_links.get("smallThumbnail"),
            "thumbnail": image_links.get("thumbnail")
       }

       # 3. Assign the new dict to the metadata key
       data["metadata"] = metadata_payload

       return data

class UserBookIngest(BaseModel):
    user_id: uuid.UUID
    book_id: uuid.UUID
    shelf_id: uuid.UUID
    reading_status: str | None 

class ReadingStatusUpdateSchema(BaseModel):
    user_book_id: uuid.UUID
    reading_status: str | None

# Data to be sent to the front end when the user wants to 
# Update their book
class BookCover(BaseModel):
    book_id: uuid.UUID
    title: str
    thumbnail: str | None 
    description: str | None 
    categories: list[str] | None = Field(default_factory=list)
    authors: list[str] = Field(default_factory=list)
    total_pages: int | None 

class UserBookCover(BaseModel):
    user_book_id: uuid.UUID
    title: str
    thumbnail: str | None
    description: str | None
    authors: list[str] = Field(default_factory=list)
    tags: list[BookTagSchema] | None

class BookSearchResult(BaseModel):
    id: uuid.UUID
    thumbnail: str | None = None
    title: str
    authors: list[str] = Field(default_factory=list)

class BookTagSchema(BaseModel):
    user_book_id: uuid.UUID
    name: str
    rating_value: int | None

    @field_validator("name")
    @classmethod
    def clean_up_name(cls, n: str) -> str:
        clean_text = re.sub(r'[^a-zA-Z0-9\s]', '', n) 
        return clean_text.strip().title()

class BookEntries(BaseModel):
    id: uuid.UUID
    entries: list[EntryPublic]
