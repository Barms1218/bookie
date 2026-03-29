import httpx
from fastapi import HTTPException

class GoogleBooksService:
    def __init__(self, api_key: str, client: httpx.AsyncClient):
        self.api_key = api_key
        self.base_url = "https://www.googleapis.com/books/v1/volumes"
        self.client = client

    async def get_book_with_term(self, term: str):
            params ={"q": f"term:{term}", "key": self.api_key}
            response = await self.client.get(self.base_url, params=params)
 
            if not response.is_success: 
                raise HTTPException(status_code=502, detail="External API Failure")

            return response.json()
