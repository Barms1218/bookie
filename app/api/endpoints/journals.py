from fastapi import HTTPException, Request, APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings 
from app.schemas.journal import JournalIngestSchema, JournalPublic
from app.dependencies import get_journal_service
from app.services.journal_service import JournalService

router = APIRouter(prefix="/journals", tags=["journals"])

@router.post("/submit", response_model=JournalPublic, status_code=201)
async def submit_journal(
        new_journal: JournalIngestSchema, 
        service: JournalService = Depends(get_journal_service)
        ):
    data = await service.submit_journal(new_journal)

    return {"data": data }
