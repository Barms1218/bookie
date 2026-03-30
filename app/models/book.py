from datetime import time, timezone
from typing import List
from typing import Optional
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Uuid
from sqlalchemy import String, JSON, func, Integer, Float
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import Relationship
import datetime

class Base(DeclarativeBase):
    pass


class Book(Base):
    __tablename__ = "books"

    id: Mapped[Uuid] = mapped_column(primary_key=True)
    isbn: Mapped[Optional[str]] = mapped_column(String(20), index=True, unique=True)
    title: Mapped[str] = mapped_column(String(255))
    authors: Mapped[List[str]] = mapped_column(JSONB)
    page_count: Mapped[int] = mapped_column(Integer, default=0)
    meta_data: Mapped[dict] = mapped_column(JSONB)

    def __repr__(self) -> str:
        return f"Book(id={self.id!r}, title={self.title!r}, authors={self.authors!r}, page_count={self.page_count!r})"


class UserBook(Base):
    __tablename__ = "user_books"

    id: Mapped[Uuid] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"))
    reading_progress: Mapped[int] = mapped_column(Integer, default=0) 
    date_completed: Mapped[Optional[datetime.datetime]]
    rating: Mapped[Float] = mapped_column(Float, default=0) 
    

    # Relationships
    user: Mapped["User"] = Relationship(back_populates="user_books")
    book: Mapped["Book"] = Relationship(back_populates="user_books")

    journal: Mapped[List["Journal"]] = Relationship(back_populates="user_book")

    __table_args__ = (
            CheckConstraint('rating >= 0 AND rating <= 5')
            )


