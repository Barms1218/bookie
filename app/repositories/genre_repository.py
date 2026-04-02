from sqlalchemy import select, or_, func
from sqlalchemy.dialects.postgresql import insert
from app.models.journal import Genre 
from sqlalchemy.ext.asyncio import AsyncSession

class GenreRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_genre(self):
        pass
