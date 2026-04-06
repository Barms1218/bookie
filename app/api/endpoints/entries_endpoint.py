from fastapi import HTTPException, Request, APIRouter, Depends
from app.dependencies import get_entry_service 
from app.schemas.entry_schemas import EntryIngestSchema, EntryPublic, EntrySearchSchema
from app.services.entry_service import EntryService

router: APIRouter = APIRouter(prefix="/entries", tags=["entries"])

@router.post("/new", response_model=EntryPublic, status_code=201)
async def new_note(schema: EntryIngestSchema, service: EntryService = Depends(get_entry_service)):
   return await service.submit_entry(schema=schema) 

@router.get("/{type}", response_model=EntryPublic, status_code=200)
async def get_type_of_entry(type: str, service: EntryService = Depends(get_entry_service)):
    pass

# TODO Endpoint to get entries filtered by type and date
@router.get("search", response_model=EntryPublic, status_code=200)
async def search_entries(
        schema: EntrySearchSchema,
        service: EntryService = Depends(get_entry_service)
        ) -> list[EntryPublic]:
    pass
