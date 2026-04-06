import httpx
from app.database.models import UserBook
from app.database.unit_of_work import UnitOfWork
from app.schemas.book_schemas import (BookIngestSchema, BookCover, BookTagSchema, 
UserBookIngest, ReadingStatusUpdateSchema, BookSearchResult, UserBookCover)
from fastapi import HTTPException
from pydantic import ValidationError
from datetime import datetime
import uuid

from app.schemas.tags import PublicTag


class GoogleBooksService:
    def __init__(self, api_key: str, client: httpx.AsyncClient, uow: UnitOfWork):
        self.api_key: str = api_key
        self.base_url: str = "https://www.googleapis.com/books/v1/volumes"
        self.client: httpx.AsyncClient = client
        self.uow: UnitOfWork = uow 

    # One day work on a feature that will get a total number of results between database
    # And API
    async def get_book_with_term(self, term: str) -> list[BookSearchResult] | None:
        valid_books = []
        async with self.uow:
                db_books = await self.uow.books.search_books_local(term) 
               
                if db_books:
                    return db_books
                params = {"q": term, "key": self.api_key}
                response = await self.client.get(self.base_url, params=params)
     
                if not response.is_success: 
                    raise HTTPException(status_code=502, detail="External API Failure")

                raw_data = response.json()

                # Google returns everything in one big items dictionary
                items = raw_data.get("items", [])

                for item in items:
                    volume_info = item.get("volumeInfo", {})
                    try:
                        book = BookIngestSchema(**volume_info)
                        saved_book = await self.uow.books.save_book_to_db(book)
                        valid_books.append(saved_book)
                    except ValidationError as e:
                        # If a book has bad data, ignore it and move on
                        print(f"Skipping book: {e}")
                        continue

                await self.uow.commit()

        return valid_books 

    async def view_book(self, book_id: uuid.UUID) -> BookCover:
        book = await self.uow.books.get_book_with_id(id=book_id)

        if not book:
            raise HTTPException(404, "No book found with that id")


        detailed_book = BookCover(
                book_id=book.id,
                title=book.title,
                thumbnail=book.meta_data.get("thumbnail"),
                description=book.meta_data.get("description"),
                categories=book.meta_data.get("categories"),
                authors=book.authors,
                total_pages=book.page_count
    
                )

        return detailed_book

    async def save_user_book(self, schema: UserBookIngest):
        return await self.uow.books.save_user_book(book_schema=schema)

    async def view_user_book_dashboard(self,user_book_id: uuid.UUID) -> UserBookCover:
        async with self.uow:    
            detailed_book = await self.uow.books.get_user_book(user_book_id=user_book_id)

            rows = await self.uow.books.get_book_tags(user_book_id=user_book_id)
            detailed_book.tags = rows 
        return detailed_book
    
    async def change_reading_status(self, schema: ReadingStatusUpdateSchema) -> str | None:
            updated_status = await self.uow.books.change_reading_status(schema=schema)
            if not updated_status:
                raise HTTPException(404, "No user book found")

            return updated_status
