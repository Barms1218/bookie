from typing import Optional, List
from sqlalchemy import select, or_, func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

class QuoteRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
