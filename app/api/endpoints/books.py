from app.dependencies import get_google_service
from fastapi import APIRouter, Depends
from app.services.book_services import GoogleBooksService

router = APIRouter(prefix="/books", tags=["books"])

@router.get("/search")
async def search_books(term: str, service: GoogleBooksService = Depends(get_google_service)):
    data = await service.get_book_with_term(term)
    return {"data": data }

