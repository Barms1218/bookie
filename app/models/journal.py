from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import DateTime, ForeignKey, String, func, Text, Integer, Boolean, Float, ARRAY, Index, Table, Column 
from sqlalchemy.orm import Mapped, mapped_column, Relationship
from .base import Base
import datetime
import uuid

if TYPE_CHECKING:
    from .user import User
    from .user_book import UserBook

class Journal(Base):
    __tablename__ = "journals"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_book_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user_books.id")) #journals belong to a book
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id")) # And a user
    content: Mapped[str] = mapped_column(String(2000)) #Limit content to 500 characters
    date_made: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now()) 
    is_private: Mapped[Boolean] = mapped_column(Boolean, default=True)
    reading_progress: Mapped[Float] = mapped_column(Float, default=0)
    vibe: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Relationships
    user: Mapped["User"] = Relationship(back_populates="journals")
    user_book: Mapped["UserBook"] = Relationship(back_populates="journals")



