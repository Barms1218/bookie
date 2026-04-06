from fastapi.responses import RedirectResponse
from app.dependencies import get_google_service
from fastapi import APIRouter, Depends, Request 
from app.schemas.book_schemas import (
        BookSearchResult, 
        BookCover,
        UserBookCover,
        UserBookIngest,
        ReadingStatusUpdateSchema)
from app.services.book_services import GoogleBooksService
import uuid

router = APIRouter(prefix="/books", tags=["books"])

@router.get("/search", response_model=list[BookSearchResult], status_code=200)
async def search_books(term: str, service: GoogleBooksService = Depends(get_google_service)):
    return await service.get_book_with_term(term)


@router.post("/select/{book_id}", response_model=BookCover, status_code=200)
async def select_listed_book(book_id: uuid.UUID, service: GoogleBooksService = Depends(get_google_service)):
    return await service.view_book(book_id=book_id)

@router.post("/add", response_model=BookCover, status_code=201)
async def add_user_book(schema: UserBookIngest, service: GoogleBooksService = Depends(get_google_service)):
    return await service.save_user_book(schema=schema)

@router.get("/view/{user_book_id}", response_model=UserBookCover, status_code=200)
async def view_book_dashboard(
user_book_id: uuid.UUID,
service: GoogleBooksService = Depends(get_google_service)):
    return await service.view_user_book_dashboard(user_book_id=user_book_id)

@router.post("/status_update", response_model=ReadingStatusUpdateSchema, status_code=200)
async def update_readingStatus(
        user_book_id: uuid.UUID,
        service: GoogleBooksService = Depends(get_google_service)):
    pass
        
