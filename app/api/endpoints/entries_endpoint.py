from fastapi import HTTPException, Request, APIRouter, Depends
from app.dependencies import get_entry_service 
from app.schemas.entry_schemas import EntryIngestSchema
from app.services.entry_service import EntryService

router: APIRouter = APIRouter(prefix="/entries", tags=["entries"])

@router.post("new/", status_code=201)
async def new_note(schema: EntryIngestSchema, service: EntryService = Depends(get_entry_service)):
   return await service.submit_entry(schema=schema) 
