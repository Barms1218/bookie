from app.core.config import settings 
from app.repositories.journal_repository import JournalRepository
from app.repositories.quote_repository import QuoteRepository
from app.services.book_services import GoogleBooksService
from app.services.journal_service import JournalService
from app.services.user_service import UserService
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

def get_book_repo(db: AsyncSession = Depends(get_db)) -> BookRepository:
    return BookRepository(db = db)

def get_user_repo(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(db = db)

def get_journal_repo(db: AsyncSession = Depends(get_db)) -> JournalRepository:
    return JournalRepository(db = db)

def get_quote_repo(db: AsyncSession = Depends(get_db)) -> QuoteRepository:
    return QuoteRepository(db = db)

def get_unit_of_work(db: AsyncSession = Depends(get_db)) -> UnitOfWork:
    return UnitOfWork(db=db)

class Base(DeclarativeBase):
    pass

def get_google_service(request: Request, uow: UnitOfWork = Depends(get_unit_of_work)) -> GoogleBooksService:
    client = request.app.state.http_client
    return GoogleBooksService(
            api_key=str(settings.google_api_key), 
            client=client,
            uow=uow)

def get_user_service(request: Request, uow: UnitOfWork = Depends(get_unit_of_work)) -> UserService:
    client = request.app.state.http_client
    return UserService(client=client, uow=uow)

def get_journal_service(request: Request, 
                        uow: UnitOfWork = Depends(get_unit_of_work)
                        ) -> JournalService:
    return JournalService(client=request.app.state.http_client, uow=uow)

class UnitOfWork:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.books = BookRepository(self.db) 
        self.users = UserRepository(self.db) 
        self.quotes = QuoteRepository(self.db) 
        self.journals = JournalRepository(self.db) 

    async def commit(self):
        await self.db.commit()

    async def rollback(self):
        await self.db.rollback()

    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback()

