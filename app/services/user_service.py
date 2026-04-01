import httpx
from fastapi import HTTPException
from app.dependencies import UnitOfWork
from app.schemas.user import UserIngestSchema, User 
from argon2 import PasswordHasher

class UserService:
    def __init__(self, client: httpx.AsyncClient, uow: UnitOfWork):
        self.client = client
        self.uow = uow 

    async def register_user(self, new_user: UserIngestSchema) -> User:
        # If the email isn't already in the database
        if self.uow.users.get_by_email(new_user.email):
            raise HTTPException(status_code=400, detail="Email already registered")

        user_data = new_user.model_dump(exclude={"password"})

        if new_user.password:
            ph = PasswordHasher()
            hashed_password = ph.hash(new_user.password.get_secret_value())
            user_data["password"] = hashed_password
        
        inserted_user = await self.uow.users.create_user(user_data)
        created_user = User(inserted_user.id, str(inserted_user.email), inserted_user.name, inserted_user.date_joined) 

        return created_user 




