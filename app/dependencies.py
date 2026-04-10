from app.core.config import settings 
from fastapi import Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase
import app.repositories as repos
import app.services as services
from app.database import engine
from app.database.unit_of_work import UnitOfWork

async def get_db():
    async with engine.async_session() as session:
            yield session

def get_book_repo(db: AsyncSession = Depends(get_db)) -> repos.BookRepository:
    return repos.BookRepository(db = db)

def get_user_repo(db: AsyncSession = Depends(get_db)) -> repos.UserRepository:
    return repos.UserRepository(db = db)

def get_entry_repo(db: AsyncSession = Depends(get_db)) -> repos.EntryRepository:
    return repos.EntryRepository(db = db)

def get_tag_repo(db: AsyncSession = Depends(get_db)) -> repos.TagRepository:
    return repos.TagRepository(db = db)

def get_unit_of_work(db: AsyncSession = Depends(get_db)) -> UnitOfWork:
    return UnitOfWork(db=db)

class Base(DeclarativeBase):
    pass

def get_book_service(
        request: Request,
        uow: UnitOfWork = Depends(get_unit_of_work)
        ) -> services.BookService:
    client = request.app.state.http_client
    return services.BookService(
            api_key=str(settings.google_api_key), 
            client=client,
            uow=uow)

def get_user_service(
        request: Request, 
        uow: UnitOfWork = Depends(get_unit_of_work)
        ) -> services.UserService:
    client = request.app.state.http_client
    return services.UserService(client=client, uow=uow)

def get_tag_service(
        request: Request,
        uow: UnitOfWork = Depends(get_unit_of_work)
        ) -> services.TagService:
    client = request.app.state.http_client
    return services.TagService(client=client, uow=uow)

def get_ai_service(
        request: Request,
        uow: UnitOfWork = Depends(get_unit_of_work)
        ) -> services.AIService:
    client = request.app.state.http_client
    return services.AIService(
            api_key=settings.gemini_api_key,
            client=client,
            uow=uow)
