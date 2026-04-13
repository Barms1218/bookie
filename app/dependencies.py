from typing import Annotated
from app.core.config import settings 
from fastapi import HTTPException, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase
import app.repositories as repos
import app.services as services
from app.database import engine
from app.database.unit_of_work import UnitOfWork
from fastapi.security import OAuth2PasswordBearer 
from app.schemas import  CurrentUser
import jwt
from jwt import InvalidTokenError
import uuid

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_db():
    async with engine.async_session() as session:
            yield session

async def get_book_repo(db: Annotated[AsyncSession, Depends(get_db)]) -> repos.BookRepository:
    return repos.BookRepository(db = db)

async def get_user_repo(db: Annotated[AsyncSession, Depends(get_db)]) -> repos.UserRepository:
    return repos.UserRepository(db = db)

async def get_entry_repo(db: Annotated[AsyncSession, Depends(get_db)]) -> repos.EntryRepository:
    return repos.EntryRepository(db = db)

async def get_tag_repo(db: Annotated[AsyncSession, Depends(get_db)]) -> repos.TagRepository:
    return repos.TagRepository(db = db)

async def get_unit_of_work(db: Annotated[AsyncSession, Depends(get_db)]) -> UnitOfWork:
    return UnitOfWork(db=db)



class Base(DeclarativeBase):
    pass

async def get_book_service(
        request: Request,
        uow: Annotated[UnitOfWork, Depends(get_unit_of_work)]
        ) -> services.BookService:
    client = request.app.state.http_client
    return services.BookService(
            api_key=str(settings.google_api_key), 
            client=client,
            uow=uow)

async def get_user_service(
        request: Request, 
        uow: Annotated[UnitOfWork, Depends(get_unit_of_work)]
        ) -> services.UserService:
    client = request.app.state.http_client
    return services.UserService(client=client, uow=uow)

async def get_tag_service(
        request: Request,
        uow: Annotated[UnitOfWork, Depends(get_unit_of_work)]
        ) -> services.TagService:
    client = request.app.state.http_client
    return services.TagService(client=client, uow=uow)

async def get_ai_service(
        request: Request,
        uow: Annotated[UnitOfWork, Depends(get_unit_of_work)]
        ) -> services.AIService:
    client = request.app.state.http_client
    return services.AIService(
            api_key=settings.gemini_api_key,
            client=client,
            uow=uow)

async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        service: Annotated[services.UserService, Depends(get_user_service)]) -> CurrentUser:
    user: CurrentUser | None = None
    credentials_exception = HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
            )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        id_str: str | None = payload.get("sub")
        if id_str is None:
            raise credentials_exception
        user_id = uuid.UUID(id_str)
    except InvalidTokenError:
        raise credentials_exception

    user = await service.get_user_by_id(user_id=user_id)

    return user
