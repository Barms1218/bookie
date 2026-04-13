from datetime import timedelta
from typing import Annotated, Any
from fastapi import Request, APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings 
from app.schemas.user import CurrentUser, UserIngestSchema, UserLoginSchema, Token
from app.services.user_service import UserService 
from app.dependencies import get_user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register", status_code=201)
async def register(new_user: UserIngestSchema, service: Annotated[UserService, Depends(get_user_service)]):
    return await service.register_user(new_user=new_user) 

@router.post("/login", response_model=CurrentUser, status_code=200)
async def login(
        service: Annotated[UserService, Depends(get_user_service)],
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = UserLoginSchema(email=form_data.username, password=form_data.password)
    logged_in_user = await service.login_user(user_login=user)
    if not logged_in_user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.expires)
    claims: dict[str, Any] = {"sub": logged_in_user.id, "email": logged_in_user.email}
    token = service.create_access_token(data=claims, expires_delta=access_token_expires)
    return Token(access_token=token, token_type="bearer")
