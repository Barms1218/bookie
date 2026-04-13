from datetime import datetime, timedelta, timezone
from typing import Any
from argon2.exceptions import VerifyMismatchError
import httpx
from fastapi import HTTPException
from app.database.unit_of_work import UnitOfWork
from argon2 import PasswordHasher
from sqlalchemy.exc import SQLAlchemyError
import app.schemas as schemas
from app.core import config
import jwt
import uuid

class UserService:
    def __init__(self, client: httpx.AsyncClient, uow: UnitOfWork):
        self.client: httpx.AsyncClient = client
        self.uow: UnitOfWork = uow 

    async def register_user(self, new_user: schemas.UserIngestSchema) -> schemas.CurrentUser:

        async with self.uow:

            if new_user.password:
                ph = PasswordHasher()
                hashed_password = ph.hash(new_user.password.get_secret_value())
                new_user.password_hash = hashed_password
                print("password hash successful") 
            try:
                inserted_user = await self.uow.users.create_user(new_user)
            except SQLAlchemyError as e:
                # This triggers if the email (Unique Constraint) is violated
                await self.uow.rollback() 
                raise HTTPException(status_code=400, detail=f"{e}")
            
            current_user = schemas.CurrentUser(id=inserted_user.id, email=inserted_user.email)

            return current_user

    async def login_user(self, user_login: schemas.UserLoginSchema) -> schemas.CurrentUser:
        user = await self.uow.users.get_by_email(email=user_login.email)

        if not user:
            raise HTTPException(401, "No user with that email")

        if not user.password_hash:
            raise HTTPException(401, "Invalid credentials.")
            
        ph = PasswordHasher()   
        try:
            _ = ph.verify(user.password_hash, 
                      user_login.password)
        except VerifyMismatchError:
            raise HTTPException(401, "Invalid credentials.")

        current_user = schemas.CurrentUser(
                id=user.id, 
                email=user.email, 
                )

        return current_user 

    async def get_user_by_email(self, email: str) -> schemas.CurrentUser:
        current_user = await self.uow.users.get_by_email(email=email)
        if not current_user:
            raise HTTPException(401, "No user with those credentials")
        return schemas.CurrentUser(id=current_user.id,email=current_user.email)

    async def get_user_by_id(self, user_id: uuid.UUID) -> schemas.CurrentUser:
        current_user = await self.uow.users.get_by_id(id=user_id)
        if not current_user:
            raise HTTPException(401, "No user with those credentials")
        return schemas.CurrentUser(id=current_user.id,email=current_user.email)


    async def create_access_token(self, data: dict[str, Any], expires_delta: timedelta | None = None): 
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=30)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, config.settings.secret_key, algorithm=config.settings.algorithm)
        return encoded_jwt





