from fastapi import Request, APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings 
from app.schemas.user import UserIngestSchema 
from app.services.user_service import UserService as service

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register")
async def register(new_user: UserIngestSchema):
    data = service.register_user(new_user=) 
    return {"data": data }

