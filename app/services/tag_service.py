import httpx
from app.database.unit_of_work import UnitOfWork
import app.schemas as schemas
from fastapi import HTTPException
from pydantic import ValidationError
from itertools import groupby
from operator import attrgetter
import uuid

class TagService:
    def __init__(self, client: httpx.AsyncClient, uow: UnitOfWork):
        self.client: httpx.AsyncClient = client
        self.uow: UnitOfWork = uow 

    async def create_new_tags(self, new_tag: schemas.TagIngestSchema) -> schemas.PublicTag:
        db_tag = await self.uow.tags.upsert_tags(new_tag=new_tag)

        return schemas.PublicTag(id=db_tag.id, name=db_tag.name)

    async def get_tags(self) -> list[schemas.AllTagsResponse]:
        db_tags = await self.uow.tags.get_all_tags()

        grouped_tags: list[schemas.AllTagsResponse] = [
                schemas.AllTagsResponse(
                    type=tag_type,
                    tags=[schemas.PublicTag.model_validate(t) for t in db_tags]
                    )
                for tag_type, tag_list in groupby(db_tags, key=attrgetter('type'))
                ]
        return grouped_tags
