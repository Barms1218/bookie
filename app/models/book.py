from typing import TYPE_CHECKING, List, Optional 
from sqlalchemy import CheckConstraint, ForeignKey, String, Integer, Float
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, Relationship
from .base import Base
import uuid
import datetime

if TYPE_CHECKING:
    from .user import User
    from .journal import Journal, Quote


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


class UserBook(Base):
    __tablename__ = "user_books"


    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    book_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("books.id"))
    current_page: Mapped[int] = mapped_column(Integer, default=0) 
    date_completed: Mapped[Optional[datetime.datetime]]
    rating: Mapped[Float] = mapped_column(Float, default=0) 
    status: str = "to-read"
    

    # Relationships
    user: Mapped["User"] = Relationship(back_populates="user_books")
    journals: Mapped[List["Journal"]] = Relationship(back_populates="user_book")
    quotes: Mapped[List["Quote"]] = Relationship(back_populates="user_book")

    __table_args__ = (
            CheckConstraint('rating >= 0 AND rating <= 5', name="rating_between_0_and_5"),
            )


