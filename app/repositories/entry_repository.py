from sqlalchemy import select, or_, func, update 
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import contains_eager, selectinload 
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import uuid
import app.schemas as schemas
import app.database.models as models

class EntryRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db: AsyncSession = db

    async def get_book_entries(self, user_book_id: uuid.UUID):
        stmt = (
            select(models.Entry)
            .where(models.Entry.user_book_id == user_book_id)
            .options(
                selectinload(models.Entry.entry_tags).selectinload(models.EntryTag.tag)
            )
        )

        result = await self.db.execute(stmt)

        return result.scalars().all()

    async def create_entry_tag(self, tags: list[schemas.EntryTagIngestSchema]):
        """

        Args:
            tags: 
        """
        payload = [tag.model_dump(exclude={'name'}) for tag in tags]

        stmt = insert(models.EntryTag).values(payload)

        upsert_stmt = stmt.on_conflict_do_update(
                index_elements=['entry_id', 'tag_id'],
                set_={'entry_id': stmt.excluded.entry_id } # Forces the row to be returned with no changes
                ).returning(models.EntryTag)

        result = await self.db.execute(upsert_stmt)

        

