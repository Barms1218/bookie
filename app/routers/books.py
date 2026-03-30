from fastapi import Request, APIRouter, Depends
from services import GoogleBooksService
from app.config import settings


router = APIRouter(prefix="/books", tags=["books"])

def get_google_service(request: Request) -> GoogleBooksService:
    client = request.app.state.http_client
    return GoogleBooksService(
            api_key=str(settings.google_api_key), 
            client=client)


@router.get("/search/{term}")
async def search_books(term: str, service: GoogleBooksService = Depends(get_google_service)):
    data = await service.get_book_with_term(term)
    return {"data": data }


