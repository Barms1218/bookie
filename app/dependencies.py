from app.core.config import settings 
from app.services.book_services import BookService
from app.services.user_service import UserService
from fastapi import Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase
from app.repositories.book_repository import BookRepository 
from app.repositories.user_repository import UserRepository 
from app.repositories.entry_repository import EntryRepository 
from app.database import engine
from app.database.unit_of_work import UnitOfWork

async def get_db():
    async with engine.async_session() as session:
            yield session

def get_book_repo(db: AsyncSession = Depends(get_db)) -> BookRepository:
    return BookRepository(db = db)

def get_user_repo(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(db = db)

def get_entry_repo(db: AsyncSession = Depends(get_db)) -> EntryRepository:
    return EntryRepository(db = db)


def get_unit_of_work(db: AsyncSession = Depends(get_db)) -> UnitOfWork:
    return UnitOfWork(db=db)

class Base(DeclarativeBase):
    pass

def get_book_service(
        request: Request,
        uow: UnitOfWork = Depends(get_unit_of_work)
        ) -> BookService:
    client = request.app.state.http_client
    return BookService(
            api_key=str(settings.google_api_key), 
            client=client,
            uow=uow)

def get_user_service(
        request: Request, 
        uow: UnitOfWork = Depends(get_unit_of_work)
        ) -> UserService:
    client = request.app.state.http_client
    return UserService(client=client, uow=uow)


