import httpx
from app.database.unit_of_work import UnitOfWork
from app.schemas.entry_schemas import EntryIngestSchema, EntryPublic
from fastapi import HTTPException

from app.schemas.tags import EntryTagIngestSchema, PublicTag


class EntryService:
    def __init__(self, client: httpx.AsyncClient, uow: UnitOfWork):
        self.client: httpx.AsyncClient = client
        self.uow: UnitOfWork = uow

    async def submit_entry(self, schema: EntryIngestSchema) -> EntryPublic:
        new_tags = []
        async with self.uow:

            entry = await self.uow.entries.create_entry(schema=schema)

            if schema.tags:
                new_tags = await self.uow.tags.create_tags(schemas=schema.tags)
            
            entry_tags: list[EntryTagIngestSchema] = [
                    EntryTagIngestSchema(
                        entry_id=entry.id,
                        tag_id= t.id,
                        name=t.name
                        )
                    for t in new_tags
                    ] 

            _ = await self.uow.tags.create_entry_tag(schemas=entry_tags) 

            entry.tags = [PublicTag(id=t.tag_id, name=t.name, rating_value=None) for t in entry_tags]

        return entry 
