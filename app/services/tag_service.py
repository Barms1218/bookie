import httpx
from app.database.unit_of_work import UnitOfWork

from app.schemas.tags import PublicTag, BookTagIngestSchema

class TagService:
    def __init__(self, client: httpx.AsyncClient, uow: UnitOfWork):
        self.client: httpx.AsyncClient = client
        self.uow: UnitOfWork = uow

    async def create_book_tags(
            self, 
            schemas: list[BookTagIngestSchema]) -> list[PublicTag]:
        book_id = schemas[0].book_id
        async with self.uow:
            try:
                tags = await self.uow.tags.create_tags(schemas)

                public_tags = await self.uow.tags.create_book_tag(
                        tags=tags,
                        book_id=book_id
                        )

            
                await self.uow.commit()
                return [PublicTag.model_validate(t) for t in public_tags] 
            except Exception:
                await self.uow.rollback()
                raise

