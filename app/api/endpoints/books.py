from app.dependencies import get_google_service
from fastapi import APIRouter, Depends
from app.schemas.book import BookSearchResult, DetailedBook
from app.services.book_services import GoogleBooksService
from typing import List

router = APIRouter(prefix="/books", tags=["books"])

@router.get("/search", response_model=BookSearchResult, status_code=200)
async def search_books(term: str, service: GoogleBooksService = Depends(get_google_service)):
    data = await service.get_book_with_term(term)
    return {"data": data }


@router.post("/library/batch-add", response_model=List[DetailedBook])
async def select_books(schemas: list[BookSearchResult]):
    pass
