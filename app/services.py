import httpx
from app.models import BookIngestSchema
from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

class GoogleBooksService:
    def __init__(self, api_key: str, client: httpx.AsyncClient, db: AsyncSession):
        self.api_key = api_key
        self.base_url = "https://www.googleapis.com/books/v1/volumes"
        self.client = client
        self.session = db

    async def get_book_with_term(self, term: str):
            params ={"q": f"term:{term}", "key": self.api_key}
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
                    valid_books.append(book)
                except ValidationError as e:
                    # If a book has bad data, ignore it and move on
                    print(f"Skipping book: {e}")
                    continue

            with self.session.connect() as conn:
                conn.execute(insert(books), valid_books)

            return valid_books 
