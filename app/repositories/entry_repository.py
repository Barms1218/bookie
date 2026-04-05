from sqlalchemy import insert_sentinel, select, or_, func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Entry
from app.schemas.entry_schemas import EntryIngestSchema, EntryPublic

class EntryRepository:
    def __init__(self, db: AsyncSession):
        self.db: AsyncSession = db

    async def create_entry(self, schema: EntryIngestSchema):
        stmt = insert(Entry).values(**schema.model_dump(exclude={"tags"}))

        upsert_stmt = stmt.on_conflict_do_update(
                index_elements=['created_on'],
                set_={
                    Entry.content: stmt.excluded.content,
                    Entry.page_number: stmt.excluded.page_number,
                    Entry.updated_on: func.now(),
                    Entry.is_private: stmt.excluded.is_private
                    }
                ).returning(Entry)

        result = await self.db.execute(upsert_stmt)

        inserted_entry = result.scalar_one()

        return EntryPublic(
                id=inserted_entry.id,
                content=inserted_entry.content,
                page=inserted_entry.page_number if inserted_entry.page_number else 0
                )

