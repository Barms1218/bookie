from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import DateTime, ForeignKey, String, func, Text, Integer 
from sqlalchemy.orm import Mapped, mapped_column, Relationship
from .base import Base
import datetime
import uuid

if TYPE_CHECKING:
    from .book import UserBook  
    from .user import User


class Journal(Base):
    __tablename__ = "journals"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_book_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user_books.id")) #journals belong to a book
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id")) # And a user
    content: Mapped[str] = mapped_column(String(2000)) #Limit content to 500 characters
    date_made: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now()) 

    # Relationships
    user: Mapped["User"] = Relationship(back_populates="journals")
    user_book: Mapped["UserBook"] = Relationship(back_populates="journals")


class Quote(Base):
    __tablename__ = "quotes"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_book_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user_books.id")) #journals belong to a book
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id")) 
    character: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    content: Mapped[str] = mapped_column(Text)
    page: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Relationships
    user: Mapped["User"] = Relationship(back_populates="quotes")
