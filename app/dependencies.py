from app.core.config import settings 
from app.repositories.journal_repository import JournalRepository
from app.repositories.quote_repository import QuoteRepository
from app.services.book_services import GoogleBooksService
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

def get_unit_of_work(db: AsyncSession =Depends(get_db),
                    books: BookRepository = Depends(get_book_repo), 
                     users: UserRepository = Depends(get_user_repo),
                     quotes: QuoteRepository = Depends(get_quote_repo),
                     journals: JournalRepository = Depends(get_journal_repo)) -> UnitOfWork:
    return UnitOfWork(db=db, books=books, users=users, quotes=quotes, journals=journals)

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

class UnitOfWork:
    def __init__(
        self, 
        db: AsyncSession,
        books: BookRepository, 
        users: UserRepository, 
        quotes: QuoteRepository,
        journals: JournalRepository):
        self.db = db
        self.books = books
        self.users = users
        self.quotes = quotes
        self.journals = journals


