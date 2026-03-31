from fastapi import Request, APIRouter, Depends
from app.services.book_services import GoogleBooksService
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings 
from app.database.engine import get_db

router = APIRouter(prefix="/books", tags=["books"])

def get_google_service(request: Request, session: AsyncSession = Depends(get_db)) -> GoogleBooksService:
    client = request.app.state.http_client
    return GoogleBooksService(
            api_key=str(settings.google_api_key), 
            client=client, db=session)


@router.get("/search/{term}")
async def search_books(term: str, service: GoogleBooksService = Depends(get_google_service)):
    data = await service.get_book_with_term(term)
    return {"data": data }

