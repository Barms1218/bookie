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
    clubs: Mapped[list["BookClub"] | None] = Relationship(
            secondary="club_members", back_populates="users")                                        



class Book(Base):
    __tablename__: str = "books"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    isbn: Mapped[str | None] = mapped_column(String(13), index=True, unique=True)
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

    # Relationships
    user: Mapped["User"] = Relationship(back_populates="user_books")
    entries: Mapped[list["Entry"] | None] = Relationship(back_populates="user_book")
    book_tags: Mapped[list["BookTag"]] = Relationship(back_populates="user_books")
    tags: AssociationProxy[Type] = association_proxy("book_tags", "tags")

    __table_args__: tuple[Any, ...] = (
            UniqueConstraint('user_id', 'book_id', name='uix_user_book'),
            CheckConstraint('rating >= 0 AND rating <= 5', name="rating_between_0_and_5"),
            )


class Entry(Base):
    __tablename__: str = "entries"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_book_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user_books.id"))

    content: Mapped[str] = mapped_column(Text)
    page_number: Mapped[int | None] = mapped_column(Integer)
    created_on: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())
    updated_on: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())
    is_private: Mapped[bool] = mapped_column(Boolean, default=True)

    user_book: Mapped["UserBook"] = Relationship(back_populates="entries")
    entry_tags: Mapped[list["EntryTag"]] = Relationship(back_populates="entries")
    tags: AssociationProxy[Type] = association_proxy("entry_tags", "tags")

class Tag(Base):
    __tablename__: str = "tags"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(50), unique=True)


    book_tags: Mapped[list["BookTag"]] = Relationship(back_populates="tag")
    entry_tags: Mapped[list["EntryTag"]] = Relationship(back_populates="tag")

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

class EntryTag(Base):
    __tablename__: str = "entry_tags"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    entry_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("entries.id"))
    tag_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tags.id"))

    meta_data: Mapped[dict[str, Any]] = mapped_column(JSONB)

    # Relationships
    entries: Mapped[list["Entry"]] = Relationship(back_populates="entry_tags")
    tag: Mapped["Tag"] = Relationship(back_populates="entry_tags")

    __table_args__: tuple[Any, ...] = (
            UniqueConstraint('entry_id', 'tag_id', name='_user_entry_tag_uc'),
            )
