from typing import List, Optional 
from sqlalchemy import String, Integer
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base
import uuid

class Book(Base):
    __tablename__ = "books"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    isbn: Mapped[Optional[str]] = mapped_column(String(20), index=True, unique=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    authors: Mapped[List[str]] = mapped_column(ARRAY(String)) 
    page_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    meta_data: Mapped[dict] = mapped_column(JSONB)

    def __repr__(self) -> str:
        return f"Book(id={self.id!r}, title={self.title!r}, authors={self.authors!r}, page_count={self.page_count!r})"


