from sqlalchemy import select, or_, func
from sqlalchemy.dialects.postgresql import insert
from app.models.tag import Tag
from app.schemas.tags import PublicTag, TagIngestSchema
from app.models.associations import BookTag, NoteTag
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

class TagRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_tags(self, schemas: list[TagIngestSchema], book_id: uuid.UUID) -> list[PublicTag]:
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
        
        tag_results = result.scalars().all()
        tags: list[PublicTag] = [
                PublicTag(id=t.id, book_id=book_id, name=t.name)
                for t in tag_results
                ]
        return tags

    async def create_book_tag(self, tag: TagIngestSchema) -> BookTag:
        stmt = (
                insert(BookTag)
                .values(
                    user_bok_id=tag.book_id,
                    tag_id=tag.id,
                    rating_value=tag.rating
                    )
                .on_conflict_do_update(
                    index_elements=['user_book_id', 'tag_id'],
                    set_={BookTag.rating_value: tag.rating }
                    )
                .returning(BookTag)
                )
        result = await self.db.execute(stmt)

        return result.scalar_one()

