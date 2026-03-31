from typing import Optional, List
from sqlalchemy import select, or_, func
from sqlalchemy.dialects.postgresql import insert
from app.schemas.user import UserIngestSchema
from app.models.user import User 
from sqlalchemy.ext.asyncio import AsyncSession

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    def begin(self):
        self.db.Begin()
