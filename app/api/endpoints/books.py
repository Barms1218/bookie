from fastapi.responses import RedirectResponse
from app.dependencies import get_google_service
from fastapi import APIRouter, Depends, Request 
from app.schemas.book import BookSearchResult, DetailedBook
from app.services.book_services import GoogleBooksService
from typing import List
import uuid

router = APIRouter(prefix="/books", tags=["books"])

@router.get("/search", response_model=BookSearchResult, status_code=200)
async def search_books(term: str, service: GoogleBooksService = Depends(get_google_service)):
    data = await service.get_book_with_term(term)
    return {"data": data }


@router.post("/library/select/{book_id}", response_model=DetailedBook)
async def select_books(book_id: uuid.UUID, service: GoogleBooksService = Depends(get_google_service)):
    return await service.view_book(book_id=book_id)

