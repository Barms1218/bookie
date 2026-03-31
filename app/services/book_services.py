import httpx
from app.repositories import book_repository
from app.schemas.book import BookIngestSchema
from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.book_repository import BookRepository 

class GoogleBooksService:
    def __init__(self, api_key: str, client: httpx.AsyncClient, repo: BookRepository):
        self.api_key = api_key
        self.base_url = "https://www.googleapis.com/books/v1/volumes"
        self.client = client
        self.repo = repo

    async def get_book_with_term(self, term: str):
            db_books = await self.repo.search_books_local(term) 
           
            if db_books:
                return db_books
            params = {"q": term, "key": self.api_key}
            response = await self.client.get(self.base_url, params=params)
 
            if not response.is_success: 
                raise HTTPException(status_code=502, detail="External API Failure")

            raw_data = response.json()

            # Google returns everything in one big items dictionary
            items = raw_data.get("items", [])

            valid_books = []
            for item in items:
                volume_info = item.get("volumeInfo", {})
                try:
                    book = BookIngestSchema(**volume_info)
                    saved_book = await self.repo.save_book_to_db(book)
                    valid_books.append(saved_book)
                except ValidationError as e:
                    # If a book has bad data, ignore it and move on
                    print(f"Skipping book: {e}")
                    continue

            return valid_books 
