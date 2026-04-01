from typing import Optional, List
from sqlalchemy import select, or_, func
from sqlalchemy.dialects.postgresql import insert
from app.models.user import User 
from sqlalchemy.ext.asyncio import AsyncSession

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, schema: dict) -> User:
        stmt = insert(User).values(**schema).returning(User)

        result = await self.db.execute(stmt)
        return result.scalar_one()
    

    async def get_by_email(self, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email)

        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() 
