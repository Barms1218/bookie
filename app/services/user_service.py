import httpx
from fastapi import HTTPException
from app.database.unit_of_work import UnitOfWork
from app.schemas.user import UserIngestSchema, UserProfile 
from argon2 import PasswordHasher
from sqlalchemy.exc import IntegrityError

class UserService:
    def __init__(self, client: httpx.AsyncClient, uow: UnitOfWork):
        self.client = client
        self.uow = uow 

    async def register_user(self, new_user: UserIngestSchema) -> UserProfile:

        async with self.uow:
            user_data = new_user.model_dump(exclude={"password"})

            if new_user.password:
                ph = PasswordHasher()
                hashed_password = ph.hash(new_user.password.get_secret_value())
                user_data["password_hash"] = hashed_password
                print("password hash successful") 
            try:
                inserted_user = await self.uow.users.create_user(user_data)
                await self.uow.commit() 
            except IntegrityError:
                # This triggers if the email (Unique Constraint) is violated
                await self.uow.rollback() 
                raise HTTPException(status_code=400, detail="Email already registered")
            print(f"DEBUG: id={inserted_user.id}, type={type(inserted_user.id)}")
            return UserProfile(id=inserted_user.id, name=inserted_user.name, email=inserted_user.email)




