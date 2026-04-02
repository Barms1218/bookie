from app.repositories.journal_repository import JournalRepository
from app.repositories.quote_repository import QuoteRepository
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.book_repository import BookRepository 
from app.repositories.user_repository import UserRepository 


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
