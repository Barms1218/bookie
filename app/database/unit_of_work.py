from sqlalchemy.ext.asyncio import AsyncSession
import app.repositories as repos


class UnitOfWork:
    def __init__(self, db: AsyncSession):
        self.db: AsyncSession = db
        self.books: repos.BookRepository = repos.BookRepository(self.db) 
        self.users: repos.UserRepository = repos.UserRepository(self.db) 
        self.entries: repos.EntryRepository = repos.EntryRepository(self.db) 
        self.tags: repos.TagRepository = repos.TagRepository(self.db)

    async def commit(self):
        await self.db.commit()

    async def rollback(self):
        await self.db.rollback()

    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback()
