from typing import Any, cast
from sqlalchemy import CursorResult, delete, select, or_, func
from sqlalchemy.dialects.postgresql import insert
from app.database.models import Tag, NoteTag, BookTag
from app.schemas.tags import PublicTag, BookTagIngestSchema 
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

class TagRepository:
    def __init__(self, db: AsyncSession):
        self.db: AsyncSession = db

    async def create_tags(
            self, 
            schemas: list[BookTagIngestSchema]) -> list[Tag]:
        tag_data = [schema.model_dump() for schema in schemas]

        stmt = insert(Tag)

        upsert_stmt = stmt.on_conflict_do_update(
                index_elements=['name'],
                set_={
                    Tag.genre: stmt.excluded.genre,
                    Tag.meta_data: stmt.excluded.meta_data
                    }
                ).returning(Tag)
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
                    "rating_value": tag.rating_value,
                    "meta_data": tag.meta_data
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
                    "meta_data": row.meta_data
                    })
                for row in rows
        ]

        return public_tags

    async def remove_book_tag(self, book_tag_id: uuid.UUID) -> bool:
        stmt = delete(BookTag).where(BookTag.id == book_tag_id)

        result = await self.db.execute(stmt)
        await self.db.commit()
        return cast(CursorResult[Any], result).rowcount > 0

