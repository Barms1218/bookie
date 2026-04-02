import httpx
import uuid
from app.database.unit_of_work import UnitOfWork

from app.schemas.tags import PublicTag, TagIngestSchema
from fastapi import HTTPException

class TagService:
    def __init__(self, client: httpx.AsyncClient, uow: UnitOfWork):
        self.uow = uow

    async def create_tags(self, schemas: list[TagIngestSchema], book_id: uuid.UUID) -> list[PublicTag]:
        async with self.uow:
            tags = await self.uow.tags.create_tags(schemas, book_id)

            for t in tags:
                await self.uow.tags.create_book_tag(tag=t)

            
            await self.uow.commit()
            return tags
