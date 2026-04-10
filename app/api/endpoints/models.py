from typing import Annotated
from app.dependencies import get_ai_service 
from fastapi import APIRouter, Depends, HTTPException, Query
from app.services.ai_service import AIService
import uuid
import app.schemas as schemas

router = APIRouter(prefix="/models", tags=['models'])

@router.get("/recommendations/{user_id}")
async def get_book_recommendations(
        user_id: uuid.UUID,
        service:  Annotated[AIService, Depends(get_ai_service)]):
    return await service.generate_book_suggestion(user_id=user_id)
