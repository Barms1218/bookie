from typing import Annotated
from app.dependencies import get_ai_service, get_current_user 
from fastapi import APIRouter, Depends 
from app.services.ai_service import AIService
import uuid
import app.schemas as schemas

router = APIRouter(prefix="/models", tags=['models'])

@router.get("/recommendations/{user_id}", response_model=list[schemas.BookRecommendation], status_code=201)
async def get_book_recommendations(
        service:  Annotated[AIService, Depends(get_ai_service)],
        current_user: Annotated[schemas.CurrentUser, Depends(get_current_user)]):
    return await service.generate_book_suggestion(user_id=current_user.id)
