from typing import Any
from argon2 import Type
from sqlalchemy import CheckConstraint, ForeignKey, String, Text, Integer, ARRAY, Index, Boolean, UniqueConstraint, func, Float, DateTime
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, Relationship
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
import uuid


class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__: str = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), index=True, unique=True)
    name: Mapped[str] = mapped_column(String(100))
    date_joined: Mapped[datetime] = mapped_column(
            DateTime(timezone=True), server_default=func.now()) 

    # --- AUTH FIELDS (All Nullable) ---
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    google_id: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    apple_id: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)

    # Relationships
    user_books: Mapped[list["UserBook"] | None] = Relationship(back_populates="user")
    journals: Mapped[list["Journal"] | None] = Relationship(back_populates="user")
    clubs: Mapped[list["BookClub"] | None] = Relationship(
            secondary="club_members", back_populates="users")                                        
    notes: Mapped[list["Note"] | None] = Relationship(back_populates="user")
    quotes: Mapped[list["Quote"] | None] = Relationship(back_populates="user")



class Book(Base):
    __tablename__: str = "books"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    isbn: Mapped[str | None] = mapped_column(String(20), index=True, unique=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    authors: Mapped[list[str]] = mapped_column(ARRAY(String)) 
    page_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    meta_data: Mapped[dict[str, Any]] = mapped_column(JSONB)

class UserBook(Base):
    __tablename__: str = "user_books"


    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    # Foreign Keys
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    book_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("books.id"))

    current_page: Mapped[int] = mapped_column(Integer, default=0) 
    deleted_at: Mapped[datetime | None] = mapped_column(
            DateTime(timezone=True), default=None) 
    rating: Mapped[int | None] = mapped_column(default=0) 
    reading_status: Mapped[str] = mapped_column(String(15), default="to-read")
    added_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now()) 

    # Relationships
    user: Mapped["User"] = Relationship(back_populates="user_books")
    journals: Mapped[list["Journal"] | None] = Relationship(back_populates="user_book")
    quotes: Mapped[list["Quote"] | None] = Relationship(back_populates="user_book")
    notes: Mapped[list["Note"] | None] = Relationship(back_populates="user_book")
    book_tags: Mapped[list["BookTag"]] = Relationship(back_populates="user_books")
    tags: AssociationProxy[Type] = association_proxy("book_tags", "tags")

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
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id")) 
    
    content: Mapped[str] = mapped_column(Text)
    page_number: Mapped[int | None] = mapped_column(Integer)
    # This is where your Tropes (Enemies-to-Lovers) live!
    note_type: Mapped[str] = mapped_column(String, default="general") 
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    # Relationships
    user: Mapped["User"] = Relationship(back_populates="notes")
    note_tags: Mapped[list["NoteTag"]] = Relationship(back_populates="notes")
    user_book: Mapped["UserBook"] = Relationship(back_populates="notes")
    tags: AssociationProxy[Type] = association_proxy("note_tags", "tags")

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


    book_tags: Mapped[list["BookTag"]] = Relationship(back_populates="tag")
    note_tags: Mapped[list["NoteTag"]] = Relationship(back_populates="tag")

class BookClub(Base):
    __tablename__: str = "book_clubs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    invite_code: Mapped[str] = mapped_column(String, index=True, unique=True)
    current_book: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("books.id"))
    favorite_book: Mapped[uuid.UUID] = mapped_column(ForeignKey("books.id"))
    created_on: Mapped[datetime] = mapped_column(
            DateTime(timezone=True), server_default=func.now())

    users: Mapped[list["User"]] = Relationship(
            secondary="club_members", back_populates="clubs")

class ClubMember(Base):
    __tablename__: str = "club_members"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    club_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("book_clubs.id"))
    role: Mapped[str] = mapped_column(String, default="member")

class BookTag(Base):
    __tablename__: str = "book_tags"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_book_id: Mapped[uuid.UUID] = mapped_column(
            ForeignKey("user_books.id"))
    tag_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tags.id"))
    rating_value: Mapped[int | None] = mapped_column(Integer)

    # Holds color, border radius, etc.
    meta_data: Mapped[dict[str, Any]] = mapped_column(JSONB)

    # Relationships
    user_books: Mapped["UserBook"] = Relationship(back_populates="book_tags")
    tag: Mapped["Tag"] = Relationship(back_populates="book_tags")


    __table_args__: tuple[Any, ...] = (
            UniqueConstraint('user_book_id', 'tag_id', name='_user_book_tag_uc'),
            )

class NoteTag(Base):
    __tablename__: str = "note_tags"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    note_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("notes.id"))
    tag_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tags.id"))
    rating_value: Mapped[float | None] = mapped_column(Float)

    meta_data: Mapped[dict[str, Any]] = mapped_column(JSONB)

    # Relationships
    notes: Mapped[list["Note"]] = Relationship(back_populates="note_tags")
    tag: Mapped["Tag"] = Relationship(back_populates="note_tags")

    __table_args__: tuple[Any, ...] = (
            UniqueConstraint('note_id', 'tag_id', name='_user_note_tag_uc'),
            )
