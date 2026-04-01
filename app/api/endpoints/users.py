from fastapi import Request, APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings 
from app.schemas.user import User, UserIngestSchema 
from app.services.user_service import UserService 
from app.dependencies import get_user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register", response_model=User, status_code=201)
async def register(new_user: UserIngestSchema, service: UserService = Depends(get_user_service)):
    data = service.register_user(new_user=new_user) 
    return {"data": data }

