from typing import TYPE_CHECKING, List
from sqlalchemy import DateTime, ForeignKey, Uuid, String, func
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
    email: Mapped[str] = mapped_column(String(255), unique=True)

    date_joined: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now()) 

    # Relationships
    user_books: Mapped[List["UserBook"]] = Relationship(back_populates="user")
    journals: Mapped[List["Journal"]] = Relationship(back_populates="user")
    clubs: Mapped[List["BookClub"]] = Relationship(secondary="club_members", back_populates="users")                                             

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.name!r})"


class Journal(Base):
    __tablename__ = "journals"


    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_book_id: Mapped[int] = mapped_column(ForeignKey("user_books.id")) #journals belong to a book
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id")) # And a user
    content: Mapped[str] = mapped_column(String(500)) #Limit content to 500 characters
    date_made: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now()) 

    # Relationships
    user: Mapped["User"] = Relationship(back_populates="journals")
    user_book: Mapped["UserBook"] = Relationship(back_populates="journals")


