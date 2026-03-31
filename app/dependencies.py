from app.core.config import settings 
from app.services.book_services import GoogleBooksService
from fastapi import Request, Depends
from app.core.config import settings
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase
from app.repositories.book_repository import BookRepository 
from app.repositories.user_repository import UserRepository 
from app.database import engine

async def get_db():
    async with engine.async_session() as session:
            yield session

class Base(DeclarativeBase):
    pass

def get_book_repo(db: AsyncSession = Depends(get_db)) -> BookRepository:
    return BookRepository(db = db)

def get_user_repo(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(db = db)

def get_google_service(request: Request, repo: BookRepository = Depends(get_book_repo)) -> GoogleBooksService:
    client = request.app.state.http_client
    return GoogleBooksService(
            api_key=str(settings.google_api_key), 
            client=client,
            repo=repo)


