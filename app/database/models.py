from typing import Any
from sqlalchemy import CheckConstraint, ForeignKey, String, Text, Integer, ARRAY, Index, Boolean, UniqueConstraint, func, Float, DateTime
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, Relationship
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings
import uuid


class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__: str = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), index=True, unique=True)
    name: Mapped[str] = mapped_column(String(100))
    date_joined: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now()) 

    # --- AUTH FIELDS (All Nullable) ---
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    google_id: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    apple_id: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)

    # Relationships
    user_books: Mapped[list["UserBook"]] = Relationship(back_populates="user")
    journals: Mapped[list["Journal"]] = Relationship(back_populates="user")
    clubs: Mapped[list["BookClub"]] = Relationship(secondary="club_members", back_populates="users")                                        
    notes: Mapped[list["Note"]] = Relationship(back_populates="user")
    quotes: Mapped[list["Quote"]] = Relationship(back_populates="user")

    def  __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.name!r})"


class Book(Base):
    __tablename__: str = "books"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    isbn: Mapped[str | None] = mapped_column(String(20), index=True, unique=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    authors: Mapped[list[str]] = mapped_column(ARRAY(String)) 
    page_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    meta_data: Mapped[dict[str, Any]] = mapped_column(JSONB)

    def __repr__(self) -> str:
        return f"Book(id={self.id!r}, title={self.title!r}, authors={self.authors!r}, page_count={self.page_count!r})"

class UserBook(Base):
    __tablename__: str = "user_books"


    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    # Foreign Keys
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    book_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("books.id"))

    current_page: Mapped[int] = mapped_column(Integer, default=0) 
    date_completed: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None) 
    rating: Mapped[int | None] = mapped_column(default=0) 
    spice_rating: Mapped[int | None] = mapped_column(default=0)
    reading_status: Mapped[str] = mapped_column(String(15), default="to-read")
    added_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now()) 
    
    # Relationships
    user: Mapped["User"] = Relationship(back_populates="user_books")
    journals: Mapped[list["Journal"]] = Relationship(back_populates="user_book")
    quotes: Mapped[list["Quote"]] = Relationship(back_populates="user_book")
    notes: Mapped[list["Note"]] = Relationship(back_populates="user_book")
    book_tags: Mapped[list["BookTag"]] = Relationship(back_populates="user_books")

    __table_args__: tuple[Any, ...] = (

            UniqueConstraint('user_id', 'book_id', name='uix_user_book'),
            CheckConstraint('rating >= 0 AND rating <= 5', name="rating_between_0_and_5"),
            )

class Journal(Base):
    __tablename__: str = "journals"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_book_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user_books.id")) #journals belong to a book
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id")) # And a user
    content: Mapped[str] = mapped_column(String(2000)) #Limit content to 500 characters
    date_made: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now()) 
    is_private: Mapped[Boolean] = mapped_column(Boolean, default=True)
    reading_progress: Mapped[float] = mapped_column(Float, default=0)
    vibe: Mapped[str | None] = mapped_column(String, nullable=True)

    # Relationships
    user: Mapped["User"] = Relationship(back_populates="journals")
    user_book: Mapped["UserBook"] = Relationship(back_populates="journals")


class Note(Base):
    __tablename__: str = "notes"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    # Foreign Keys
    user_book_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user_books.id"))
    trope_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tags.id"))
    
    content: Mapped[str] = mapped_column(Text)
    page_number: Mapped[int | None] = mapped_column(Integer)
    # This is where your Tropes (Enemies-to-Lovers) live!
    note_type: Mapped[str] = mapped_column(String, default="general") 
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    tags: Mapped[list["Tag"]] = Relationship(secondary="note_tags",back_populates="notes")

    user: Mapped["User"] = Relationship(back_populates="notes")

class Quote(Base):
    __tablename__: str = "quotes"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_book_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user_books.id")) #journals belong to a book
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id")) 
    characters: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    content: Mapped[str] = mapped_column(Text)
    page: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Relationships
    user: Mapped["User"] = Relationship(back_populates="quotes")
    user_book: Mapped["UserBook"] = Relationship(back_populates="quotes")

    __table_args__: tuple[Any, ...]  = (
                # Indexes
            Index("ix_quotes_characters_gin", "characters", postgresql_using="gin"),
            )

class Tag(Base):
    __tablename__: str = "tags"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    genre: Mapped[str] = mapped_column(String(20))
    rating_value: Mapped[int | None] = mapped_column(Integer)
    meta_data: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)

    # Relationships
    notes: Mapped[list["Note"]] = Relationship(secondary="note_tags", back_populates="tags")    
    user_books: Mapped[list["UserBook"]] = Relationship(secondary="book_tags", back_populates="tags")

class BookClub(Base):
    __tablename__: str = "book_clubs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    invite_code: Mapped[str] = mapped_column(String, index=True, unique=True)
    current_book: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("books.id"))
    favorite_book: Mapped[uuid.UUID] = mapped_column(ForeignKey("books.id"))
    created_on: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    users: Mapped[list["User"]] = Relationship(secondary="club_members", back_populates="clubs")

class ClubMember(Base):
    __tablename__: str = "club_members"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    club_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("book_clubs.id"))
    role: Mapped[str] = mapped_column(String, default="member")

class BookTag(Base):
    __tablename__: str = "book_tags"

    user_book_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user_books.id"), primary_key=True)
    tag_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tags.id"), primary_key=True)
    rating_value: Mapped[int] = mapped_column(Integer)

    # Holds color, border radius, etc.
    meta_data: Mapped[dict[str, Any]] = mapped_column(JSONB)

    # Relationships
    user_books: Mapped["UserBook"] = Relationship(back_populates="book_tags")
    tag: Mapped["Tag"] = Relationship(back_populates="book_links")

class NoteTag(Base):
    __tablename__: str = "note_tags"

    note_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("notes.id"), primary_key=True)
    tag_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tags.id"), primary_key=True)
    rating_value: Mapped[float | None] = mapped_column(Float)

    meta_data: Mapped[dict[str, Any]] = mapped_column(JSONB)

    # Relationships
    user_books: Mapped["UserBook"] = Relationship(back_populates="book_tags")
    tag: Mapped["Tag"] = Relationship(back_populates="book_links")

