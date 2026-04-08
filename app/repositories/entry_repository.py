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

    async def get_book_entries(self, user_book_id: uuid.UUID, type: str) -> list[models.Entry]:
        stmt = (
            select(models.Entry)
            .where(models.Entry.user_book_id == user_book_id)
            .where(models.Entry.type == type)
            .options(
                selectinload(models.Entry.entry_tags).selectinload(models.EntryTag.tag)
            )
        )

        result = await self.db.execute(stmt)

        return list(result.scalars().all())

    async def create_entry_tag(self, tags: list[schemas.EntryTagIngestSchema]) -> list[models.EntryTag]:
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

        return list(result.scalars().all())

    async def get_entries_with_params(self, search_schema: schemas.EntrySearchSchema) -> list[models.Entry]:
        stmt = select(models.Entry).where(models.Entry.user_book_id == search_schema.user_book_id)

        stmt = stmt.where(models.Entry.type == search_schema.type)

        if search_schema.tag_names:
            stmt = (stmt.join(models.EntryTag, models.Entry.id == models.EntryTag.entry_id)
            .join(models.Tag, models.EntryTag.tag_id == models.Tag.id)
            .where(models.Tag.name.in_(search_schema.tag_names)))

        if search_schema.content:
            stmt = stmt.where(models.Entry.ts_vector.match(search_schema.content))

        if search_schema.dates:
            stmt = stmt.where(models.Entry.created_on.between(search_schema.dates[0], search_schema.dates[1]))

        stmt = stmt.options(selectinload(models.Entry.entry_tags).selectinload(models.EntryTag.tag))
        results = await self.db.execute(stmt)

        return list(results.scalars().all())

