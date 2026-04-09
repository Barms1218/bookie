from typing import ClassVar, TypedDict, Any
from pydantic import BaseModel, Field, ConfigDict, model_validator, field_validator
from datetime import datetime
import uuid
import re

from app.schemas.entry_schemas import EntryPublic

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
    authors: list[str] | str = "" # Make sure every model has its own list
    page_count: int = Field(default=0, alias="pageCount")
    description: str | None = None 
    
    meta_data: BookMetadata = Field(alias="metadata")

    @field_validator("authors", mode="before")
    @classmethod
    def flatten_authors(cls, v):
        if isinstance(v, list):
            # Join with a comma if it's a list, or return empty string if list is empty
            return ", ".join(v) if v else ""
        if v is None:
            return ""
        # Ensure it's a string just in case it's some other weird type
        return str(v)

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
    """
    The expected json request when a user is adding a book to their library
    Args:
        user_id: 
        book_id: 
        shelf_id:
        reading_status:
        tags: A schema requiring a user book id, a name, and a rating_value

    Returns:
    """
    custom_title: str = Field(alias="title")
    user_id: uuid.UUID
    book_id: uuid.UUID
    shelf_id: uuid.UUID | None = None
    reading_status: str | None 
    tags: list[BookTagIngestSchema] | None = Field(default_factory=list)

    @field_validator("custom_title")
    @classmethod
    def clean_title(cls, t: str) -> str:
        return t.strip().title()

class BookTagDisplay(BaseModel):
    id: uuid.UUID
    name: str
    rating_value: int | None


class BookCover(BaseModel):
    book_id: uuid.UUID
    title: str
    thumbnail: str | None 
    description: str | None 
    categories: list[str] | None = Field(default_factory=list)
    authors: str
    total_pages: int | None 

# TODO There needs to be a model to hold user book appearance data
# such as color, height, width, etc.
class UserBookCover(BaseModel):
    user_book_id: uuid.UUID
    title: str
    thumbnail: str | None
    description: str | None
    authors: str
    tags: list[BookTagDisplay] | None

class BookSearchResult(BaseModel):
    id: uuid.UUID
    thumbnail: str | None = None
    title: str
    authors: str

class BookTagIngestSchema(BaseModel):
    user_book_id: uuid.UUID
    tag_id: uuid.UUID
    rating_value: int | None

class BookRecommendSchema(BaseModel):
    title: str
    overall_rating: int
    book_tags: list[BookTag]

class BookTag(BaseModel):
    name: str
    rating_value: int | None

