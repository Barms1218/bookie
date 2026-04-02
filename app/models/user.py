from __future__ import annotations
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, Relationship
from .base import Base
import datetime
import uuid

if TYPE_CHECKING:
    from .journal import Journal
    from .user_book import UserBook
    from .book_clubs import BookClub
    from .note import Note
    from .quote import Quote

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), index=True, unique=True)
    name: Mapped[str] = mapped_column(String(100))
    date_joined: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now()) 

    # --- AUTH FIELDS (All Nullable) ---
    password_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    google_id: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True)
    apple_id: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True)

    # Relationships
    user_books: Mapped[List["UserBook"]] = Relationship(back_populates="user")
    journals: Mapped[List["Journal"]] = Relationship(back_populates="user")
    clubs: Mapped[List["BookClub"]] = Relationship(secondary="club_members", back_populates="users")                                        
    notes: Mapped[List["Note"]] = Relationship(back_populates="user")
    quotes: Mapped[List["Quote"]] = Relationship(back_populates="user")

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.name!r})"



