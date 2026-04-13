from sqlalchemy import select, or_, func
from sqlalchemy.dialects.postgresql import insert
from app.database.models import User 
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.schemas.user import UserIngestSchema

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db: AsyncSession = db

    async def create_user(self, schema: UserIngestSchema) -> User:
        stmt = insert(User).values(schema.model_dump(exclude={"password"})).returning(User)

        result = await self.db.execute(stmt)
        return result.scalar_one()
    

    async def get_by_email(self, email: str) -> User | None: 
        stmt = select(User).where(User.email == email)

        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() 

    async def get_by_id(self, id: uuid.UUID) -> User | None:
        stmt = select(User).where(User.id == id)

        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
