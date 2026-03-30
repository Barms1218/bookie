from datetime import time, timezone
from typing import List
from typing import Optional
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Uuid
from sqlalchemy import String, JSON, func, Integer, Float
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import Relationship
import datetime

class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[Uuid] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True)

    date_joined: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now()) 

    # Relationships
    user_books: Mapped[List["UserBook"]] = Relationship(back_populates="user")
    journals: Mapped[List["Journal"]] = Relationship(back_populates="users")
    clubs: Mapped[List["BookClub"]] = Relationship(secondary="club_members", back_populates="user")                                             

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.name!r})"

class Book(Base):
    __tablename__ = "books"

    id: Mapped[Uuid] = mapped_column(primary_key=True)
    isbn: Mapped[Optional[str]] = mapped_column(String(20), index=True, unique=True)
    title: Mapped[str] = mapped_column(String(255))
    authors: Mapped[List[str]] = mapped_column(JSON)
    page_count: Mapped[int] = mapped_column(Integer, default=0)

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


class Journal(Base):
    __tablename__ = "journals"

    id: Mapped[Uuid] = mapped_column(primary_key=True)
    user_book_id: Mapped[int] = mapped_column(ForeignKey("user_books.id")) #journals belong to a book
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id")) # And a user
    content: Mapped[str] = mapped_column(String(500)) #Limit content to 500 characters
    date_made: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now()) 

    # Relationships
    user: Mapped["User"] = Relationship(back_populates="journals")
    user_book: Mapped["UserBook"] = Relationship(back_populates="journals")


class BookClub(Base):
    __tablename__ = "book_clubs"

    id: Mapped[Uuid] = mapped_column(primary_key=True)
    invite_code: Mapped[str] = mapped_column(String, index=True, unique=True)
    current_book: Mapped[Optional[Uuid]] = mapped_column(ForeignKey("books.id"))
    favorite_book: Mapped[Uuid] = mapped_column(ForeignKey("books.id"))
    created_on: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    users: Mapped[List["User"]] = Relationship(back_populates="clubs")

class ClubMember(Base):
    __tablename__ = "club_members"

    id: Mapped[Uuid] = mapped_column(primary_key=True)
    user_id: Mapped[Uuid] = mapped_column(ForeignKey("users.id"))
    club_id: Mapped[Uuid] = mapped_column(ForeignKey("book_clubs.id"))
    role: Mapped[str] = mapped_column(String, default="member")
