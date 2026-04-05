from app.repositories.entry_repository import EntryRepository
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.book_repository import BookRepository 
from app.repositories.tag_repository import TagRepository
from app.repositories.user_repository import UserRepository 


class UnitOfWork:
    def __init__(self, db: AsyncSession):
        self.db: AsyncSession = db
        self.books: BookRepository = BookRepository(self.db) 
        self.users: UserRepository = UserRepository(self.db) 
        self.entries: EntryRepository = EntryRepository(self.db) 
        self.tags: TagRepository = TagRepository(self.db)

    async def commit(self):
        await self.db.commit()

    async def rollback(self):
        await self.db.rollback()

    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback()
