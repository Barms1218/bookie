from typing import TYPE_CHECKING, List
from sqlalchemy import DateTime, ForeignKey, String, func, Boolean
from sqlalchemy.orm import Mapped, mapped_column, Relationship
from .base import Base
import datetime
import uuid

if TYPE_CHECKING:
    from .book import UserBook  
    from .book_clubs import BookClub

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100))
    date_joined: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now()) 

    # Relationships
    user_books: Mapped[List["UserBook"]] = Relationship(back_populates="user")
    journals: Mapped[List["Journal"]] = Relationship(back_populates="user")
    clubs: Mapped[List["BookClub"]] = Relationship(secondary="club_members", back_populates="users")                                             
    credentials: Mapped["Credentials"] = Relationship(back_populates="user", uselist=False)

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.name!r})"


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

class Credentials(Base):
    __tablename__ = "credentials"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), unique=True) 
    email: Mapped[str] = mapped_column(String(255), index=True, unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, index=True, default=True)

    # Relationships
    user: Mapped["User"] = Relationship(back_populates="credentials")
