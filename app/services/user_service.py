import httpx
from app.repositories.user_repository import UserRepository
from fastapi import HTTPException
from app.schemas.user import UserIngestSchema, User, Credentials
from pydantic import field_validator, EmailStr, SecretStr

class UserService:
    def __init__(self, client: httpx.AsyncClient, repo: UserRepository):
        self.client = client
        self.repo = repo
    # Need to make sure email doesn't already exist in database
    # If not, need to create user with name, and \k
    async def register_user(self, new_user: UserIngestSchema) -> User:
        # If the email isn't already in the database
        
        async with self.repo.begin():
            user = User(name=new_user.name)
            self.repo.add(user)

            await self.session.flush()

            new_creds = Credentials(email=new_user.email, password=new_user.password)
            self.session.add(new_creds)
        
        inserted_user = self.repo.create_user(new_user)

        return user




