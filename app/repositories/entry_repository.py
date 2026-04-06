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
                index_elements=['user_book_id','created_on'],
                set_={
                    Entry.content: stmt.excluded.content,
                    Entry.page_number: stmt.excluded.page_number,
                    Entry.updated_on: func.now(),
                    Entry.is_private: stmt.excluded.is_private
                    }
                ).returning(Entry)

        result = await self.db.execute(upsert_stmt)

        return result.scalar_one()

            # async def get_quotes(self) -> list[EntryPublic]:
    #     pass
