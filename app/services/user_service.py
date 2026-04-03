import httpx
from fastapi import HTTPException
from app.database.unit_of_work import UnitOfWork
from app.schemas.user import UserIngestSchema, UserProfile 
from argon2 import PasswordHasher
from sqlalchemy.exc import IntegrityError

class UserService:
    def __init__(self, client: httpx.AsyncClient, uow: UnitOfWork):
        self.client: httpx.AsyncClient = client
        self.uow: UnitOfWork = uow 

    async def register_user(self, new_user: UserIngestSchema) -> UserProfile:

        async with self.uow:

            if new_user.password:
                ph = PasswordHasher()
                hashed_password = ph.hash(new_user.password.get_secret_value())
                new_user.password_hash = hashed_password
                print("password hash successful") 
            try:
                inserted_user = await self.uow.users.create_user(new_user)
                await self.uow.commit() 
            except IntegrityError:
                # This triggers if the email (Unique Constraint) is violated
                await self.uow.rollback() 
                raise HTTPException(status_code=400, detail="Email already registered")

            return UserProfile(id=inserted_user.id, name=inserted_user.name, email=inserted_user.email)




