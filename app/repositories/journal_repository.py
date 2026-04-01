from sqlalchemy import select, or_, func
from sqlalchemy.dialects.postgresql import insert
from app.models.journal import Journal
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.journal import JournalPublic

class JournalRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_journal(self, schema: dict, book_title: str) -> JournalPublic:
        stmt = insert(Journal).values(**schema).returning(Journal)

        result = await self.db.execute(stmt)
        new_journal: JournalPublic
        inserted_journal = result.scalar_one()
        
        new_journal = JournalPublic(
                id=inserted_journal.id,
                book_title=book_title,
                content=inserted_journal.content, 
                date_made=inserted_journal.date_made,
                vibe=inserted_journal.vibe
                )
        return  new_journal
