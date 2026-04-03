import uuid
from fastapi import Request, APIRouter, Depends
from app.services.tag_service import TagService
from app.dependencies import get_tag_service
from app.schemas.tags import PublicTag, BookTagIngestSchema

router = APIRouter(prefix="/tags", tags=['tags'])

@router.post(path="/add", response_model=list[PublicTag], status_code=201)
async def add_booktag_endpoint(
        schemas: list[BookTagIngestSchema],
        service: TagService = Depends(get_tag_service)
        ) -> list[PublicTag]:
    return await service.create_book_tags(schemas=schemas)


@router.delete(path="/delete/{book_tag_id}", status_code=200)
async def remote_booktag_endpoint(
                book_tag_id: uuid.UUID,
                service: TagService = Depends(get_tag_service)):
         result = await service.remove_book_tag(book_tag_id=book_tag_id)
         return {"Tag Deleted": result}
