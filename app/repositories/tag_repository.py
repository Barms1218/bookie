from operator import index
from sqlalchemy import select, or_, func
from sqlalchemy.dialects.postgresql import insert
from app.database.models import Tag, NoteTag, BookTag
from app.schemas.tags import PublicTag, TagAssignment, TagIngestSchema, TagInternal
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

class TagRepository:
    def __init__(self, db: AsyncSession):
        self.db: AsyncSession = db

    async def create_tags(self, schemas: list[TagIngestSchema]) -> list[PublicTag]:
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
        
        tag_results = list(result.scalars().all())

        public_tags: list[PublicTag] = [
                PublicTag(id=t.id, name=t.name, rating_value=t.rating_value,meta_data=t.meta_data)
                for t in tag_results
                ]
        return public_tags
            

    async def create_book_tag(self, tag: PublicTag, book_id: uuid.UUID) -> BookTag:
        stmt = insert(BookTag).values(
                user_book_id=book_id,
                tag_id=tag.id,
                rating=tag.rating_value
                )

        upsert_stmt = stmt.on_conflict_do_update(
                index_elements=['tag_id', 'book_id'],
                set_={
                    BookTag.rating_value: stmt.excluded.rating
                    }
                ).returning(BookTag)
        result = await self.db.execute(upsert_stmt)
        return result.scalar_one()

