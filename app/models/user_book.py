from __future__ import annotations
from typing import TYPE_CHECKING, List, Optional 
from sqlalchemy import CheckConstraint, UniqueConstraint, ForeignKey, String, Integer, Float
from sqlalchemy import ForeignKey, String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, Relationship
from .base import Base
import uuid
import datetime

if TYPE_CHECKING:
    from .user import User
    from .journal import Journal
    from .quote import Quote
    from .note import Note
    from .tag import Tag
    from .associations import BookTag

class UserBook(Base):
    __tablename__ = "user_books"


    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    # Foreign Keys
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    book_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("books.id"))
    genre_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("genres.id"))

    current_page: Mapped[int] = mapped_column(Integer, default=0) 
    date_completed: Mapped[Optional[datetime.datetime]]
    rating: Mapped[Float] = mapped_column(Float, default=0) 
    spice_rating: Mapped[Optional[float]] = mapped_column(Float,default=0)
    reading_status: Mapped[str] = mapped_column(String(15), default="to-read")
    added_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now()) 
    
    # Relationships
    user: Mapped["User"] = Relationship(back_populates="user_books")
    journals: Mapped[List["Journal"]] = Relationship(back_populates="user_book")
    quotes: Mapped[List["Quote"]] = Relationship(back_populates="user_book")
    notes: Mapped[List["Note"]] = Relationship(back_populates="user_book")
    tags: Mapped[List["Tag"]] = Relationship(secondary="book_tags", back_populates="user_books") 
    book_tags: Mapped[list["BookTag"]] = Relationship(back_populates="user_books")

    __table_args__ = (

            UniqueConstraint('user_id', 'book_id', name='uix_user_book'),
            CheckConstraint('rating >= 0 AND rating <= 5', name="rating_between_0_and_5"),
            )


