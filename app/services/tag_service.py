import httpx
from app.database.unit_of_work import UnitOfWork
import app.schemas as schemas
from fastapi import HTTPException
from pydantic import ValidationError
import uuid

class TagService:
    def __init__(self, client: httpx.AsyncClient, uow: UnitOfWork):
        self.client: httpx.AsyncClient = client
        self.uow: UnitOfWork = uow 

    async def create_new_tags(self, new_tag: schemas.TagIngestSchema) -> schemas.PublicTag:
        db_tag = await self.uow.tags.upsert_tags(new_tag=new_tag)

        return schemas.PublicTag(id=db_tag.id, name=db_tag.name, type=db_tag.type)
