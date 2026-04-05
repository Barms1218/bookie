from typing import Any, cast
from sqlalchemy import CursorResult, delete, select, or_, func
from sqlalchemy.dialects.postgresql import insert
from app.database.models import Tag, EntryTag, BookTag
from app.schemas.entry_schemas import TagIngestSchema
from app.schemas.tags import EntryTagIngestSchema, PublicTag 
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

class TagRepository:
    def __init__(self, db: AsyncSession):
        self.db: AsyncSession = db

    async def create_tags(
            self, 
            schemas: list[TagIngestSchema]) -> list[Tag]:
        tag_data = [schema.model_dump() for schema in schemas]

        stmt = insert(Tag)

        upsert_stmt = stmt.on_conflict_do_nothing(index_elements=['name'])
        result = await self.db.execute(upsert_stmt, tag_data)
        
        return list(result.scalars().all())

    async def create_book_tag(
            self,
            tags: list[Tag],
            book_id: uuid.UUID) -> list[PublicTag]:
        payload  = [
                {
                    "user_book_id": book_id,
                    "tag_id": tag.id,
                    }
                for tag in tags
                ]
        stmt = insert(BookTag)

        upsert_stmt = stmt.on_conflict_do_update(
                index_elements=['tag_id', 'user_book_id'],
                set_={
                    BookTag.rating_value: stmt.excluded.rating_value,
                    BookTag.meta_data: stmt.excluded.meta_data
                    }
                ).returning(BookTag)
        results = await self.db.execute(upsert_stmt, payload)
        rows = list(results.scalars().all())
        tag_names = {tag.id: tag.name for tag in tags}

        public_tags: list[PublicTag] = [
                PublicTag.model_validate({
                    "id": row.id,
                    "name": tag_names[row.tag_id],
                    "rating_value": row.rating_value,
                    })
                for row in rows
        ]

        return public_tags

    async def create_entry_tag(self, schemas: list[EntryTagIngestSchema]):
         payload = [
                 {
                     "note_id": tag.entry_id,
                     "tag_id": tag.tag_id,
                     "name": tag.name,
                     }
                 for tag in schemas
                 ]

         stmt = insert(EntryTag).values(payload)

         upsert_stmt = stmt.on_conflict_do_nothing(
                 index_elements=['note_id', 'tag_id']
                 ).returning(EntryTag)

         _ = await self.db.execute(upsert_stmt)


    async def remove_book_tag(self, book_tag_id: uuid.UUID) -> bool:
            stmt = delete(BookTag).where(BookTag.id == book_tag_id)

            result = await self.db.execute(stmt)
            await self.db.commit()
            return cast(CursorResult[Any], result).rowcount > 0

