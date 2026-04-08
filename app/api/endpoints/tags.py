from typing import Annotated
from app.dependencies import get_tag_service
from fastapi import APIRouter, Depends, HTTPException, Query
from app.services.tag_service import TagService
import uuid
import app.schemas as schemas

router = APIRouter(prefix="/tags", tags=['tags'])

@router.post("/create/{name}/{type}", response_model=schemas.PublicTag, status_code=201)
async def create_tag(name: str, type: str, service: Annotated[TagService, Depends(get_tag_service)]):
    return service.create_new_tags(new_tag=schemas.TagIngestSchema(name=name, type=type))
