from typing import Any
from sqlalchemy import CheckConstraint, Column, Enum, ForeignKey, String, Text, Integer, Index, Boolean, UniqueConstraint, func, Float, DateTime, Computed
from datetime import datetime
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR, ARRAY
from sqlalchemy.dialects.postgresql.ext import to_tsvector
from sqlalchemy.orm import Mapped, mapped_column, Relationship
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
import sqlalchemy as sa
import uuid
import enum

class EntryType(str, enum.Enum):
    note = "note"
    quote = "quote"
    journal = "journal"


class ReadingStatus(str, enum.Enum):
    want_to_read = "Want To Read"
    reading = "Reading"
    finished = "Finished"
    re_reading = "Re-Reading"
    did_not_finish = "Did Not Finish"

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__: str = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), index=True, unique=True)
    name: Mapped[str] = mapped_column(String(100))
    date_joined: Mapped[datetime] = mapped_column(
            DateTime(timezone=True), server_default=func.now()) 
    updated_at: Mapped[datetime] = mapped_column(
            DateTime(timezone=True),
            server_default=func.now(),
            default=func.now(),
            onupdate=func.now())

    # --- AUTH FIELDS (All Nullable) ---
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    google_id: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    apple_id: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)

    # Relationships
    user_books: Mapped[list["UserBook"] | None] = Relationship(back_populates="user", cascade="all, delete-orphan")
    book_cases: Mapped[list["BookCase"]] = Relationship(back_populates="user", cascade="all, delete-orphan")
    recommendations: Mapped[list["BookRecommendation"]] = Relationship(back_populates="user")
    # Path 1: Direct access to clubs (User.clubs)
    clubs: Mapped[list["BookClub"]] = Relationship(
        "BookClub", 
        secondary="club_members", 
        back_populates="members",
        viewonly=True # Tell SQLAlchemy this is for reading only to avoid conflicts
    )

    # Path 2: Access via the association object (User.club_associations)
    club_associations: Mapped[list["ClubMember"]] = Relationship("ClubMember", back_populates="user")

class Book(Base):
    __tablename__: str = "books"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    isbn: Mapped[str | None] = mapped_column(String(13), index=True, unique=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    authors: Mapped[list[str]] = mapped_column(ARRAY(String)) 
    page_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    description: Mapped[str] = mapped_column(Text, server_default='')
    ts_vector: Mapped[str] = mapped_column(
        TSVECTOR, 
        sa.Computed(
            "setweight(to_tsvector('english'::regconfig, coalesce(title, '')), 'A') || "
            "setweight(to_tsvector('english'::regconfig, array_to_string(authors, ' ')), 'B') || "
            "setweight(to_tsvector('english'::regconfig, coalesce(description, '')), 'C')",
            persisted=True
        )
    )
    updated_at: Mapped[datetime] = mapped_column(
                DateTime(timezone=True), server_default=func.now(),
                onupdate=func.now())

    meta_data: Mapped[dict[str, Any]] = mapped_column(JSONB)


    __table_args__: tuple[Any, ...] = (
            Index('ix_tx_vector', 'ts_vector', postgresql_using='gin'),
            Index('ix_book_authors', 'authors', postgresql_using='gin')
            )

class BookRecommendation(Base):
    __tablename__: str = "book_recommendations"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(255))
    authors: Mapped[list[str]] = mapped_column(ARRAY(String))
    reason: Mapped[str] = mapped_column(Text, server_default='Based on your reading history.')
    created_at: Mapped[datetime] = mapped_column(
            DateTime(timezone=True), server_default=func.now()
            )


    # Relationships
    user: Mapped["User"] = Relationship(back_populates="recommendations")

    __table_args__: tuple[Any, ...] = (
        UniqueConstraint('user_id', 'title', name='_user_book_recommendation_uc'),
    )


class UserBook(Base):
    __tablename__: str = "user_books"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    # Foreign Keys
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    book_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("books.id"))
    shelf_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("shelves.id"), nullable=True)
    custom_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    deleted_at: Mapped[datetime | None] = mapped_column(
            DateTime(timezone=True), default=None, nullable=True) 
    reading_status: Mapped[ReadingStatus] = mapped_column(Enum(ReadingStatus, name="reading_status"), nullable=False)
    overall_rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    search_vector: Mapped[str] = mapped_column(
            TSVECTOR,
            sa.Computed("to_tsvector('english', custom_title)",
                        persisted=True)
            )


    # Relationships
    user: Mapped["User"] = Relationship(back_populates="user_books")
    entries: Mapped[list["Entry"] | None] = Relationship(back_populates="user_book", cascade="all, delete-orphan")
    book_tags: Mapped[list["BookTag"]] = Relationship(back_populates="user_books", cascade="all, delete-orphan")
    tags: AssociationProxy[list["Tag"]] = association_proxy("book_tags", "tags")
    shelf: Mapped["Shelf"] = Relationship(back_populates="user_books")
    book: Mapped["Book"] = Relationship()

    __table_args__: tuple[Any, ...] = (
            UniqueConstraint('user_id', 'book_id', name='uix_user_book'),
            )

class BookCase(Base):
    __tablename__: str = "book_cases"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    user: Mapped["User"] = Relationship(back_populates="book_cases")
    shelves: Mapped[list["Shelf"]] = Relationship(back_populates="book_case", cascade="all, delete-orphan")

class Shelf(Base):
    __tablename__: str = "shelves"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    bookcase_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("book_cases.id", ondelete="CASCADE"))
    positions: Mapped[int] = mapped_column(Integer)
    capacity: Mapped[int] = mapped_column(Integer, default=1500)

    book_case: Mapped["BookCase"] = Relationship(back_populates="shelves")
    user_books: Mapped[list["UserBook"]] = Relationship(back_populates="shelf")

class Entry(Base):
    __tablename__: str = "entries"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_book_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user_books.id", ondelete="CASCADE"))

    content: Mapped[str] = mapped_column(Text)
    ts_vector: Mapped[str] = mapped_column(
            TSVECTOR, 
            sa.Computed("to_tsvector('english', content)", persisted=True))
    page: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
            DateTime(timezone=True), server_default=func.now()
            )
    updated_at: Mapped[datetime] = mapped_column(
            DateTime(timezone=True), server_default=func.now(),
            onupdate=func.now())
    deleted_at: Mapped[datetime | None] = mapped_column(
            DateTime(timezone=True), nullable=True
            )
    chapter: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    is_private: Mapped[bool] = mapped_column(Boolean, default=True)
    type: Mapped[EntryType] = mapped_column(Enum(
        EntryType, name="entrytype"), nullable=False)

    user_book: Mapped["UserBook"] = Relationship(back_populates="entries")
    entry_tags: Mapped[list["EntryTag"]] = Relationship(back_populates="entry", cascade="all, delete-orphan" )
    tags: AssociationProxy[list["Tag"]] = association_proxy("entry_tags", "tags")

    __table_args__: tuple[Any, ...] = (
            UniqueConstraint('user_book_id', 'created_at', name='entry_created_on'),
            Index('ix_entries_tx_vector', 'ts_vector', postgresql_using='gin'),
            Index('ix_entries_user_book_page', 'user_book_id', 'page'),
            Index('ix_entries_user_book_chapter', 'user_book_id', 'chapter')
            )

class Tag(Base):
    __tablename__: str = "tags"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    type: Mapped[str] = mapped_column(String(20), index=True)
    created_at: Mapped[str] = mapped_column(
    DateTime(timezone=True),
     server_default=func.now()
     )
    updated_at: Mapped[str] = mapped_column(DateTime(
        timezone=True),
        server_default=func.now(),
        onupdate=func.now()
        )
    deleted_at: Mapped[datetime | None] = mapped_column(
            DateTime(timezone=True), default=None, nullable=True)
    book_tags: Mapped[list["BookTag"]] = Relationship(back_populates="tag", cascade="all, delete-orphan")
    entry_tags: Mapped[list["EntryTag"]] = Relationship(back_populates="tag", cascade="all, delete-orphan")

class BookClub(Base):
    __tablename__: str = "book_clubs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    invite_code: Mapped[str] = mapped_column(String, index=True, unique=True)
    current_book: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("books.id"), nullable=True)
    favorite_book: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("books.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
            DateTime(timezone=True), server_default=func.now())

    # Path 1: Direct access to members (BookClub.members)
    members: Mapped[list["User"]] = Relationship(
            "User", 
            secondary="club_members", 
            back_populates="clubs",
            # Added 'club' and 'member_associations' to the overlaps list
            overlaps="club_associations,user,club,member_associations" 
    )

    # Path 2: Access via the association object
    member_associations: Mapped[list["ClubMember"]] = Relationship("ClubMember", back_populates="club")

class ClubMember(Base):
    __tablename__: str = "club_members"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), primary_key=True)
    club_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("book_clubs.id", ondelete="CASCADE"), primary_key=True)
    role: Mapped[str] = mapped_column(String, default="member")

    user: Mapped["User"] = Relationship("User", back_populates="club_associations", overlaps="clubs, club_members")
    club: Mapped["BookClub"] = Relationship("BookClub", back_populates="member_associations", overlaps="clubs, club_members")

class BookTag(Base):
    __tablename__: str = "book_tags"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_book_id: Mapped[uuid.UUID] = mapped_column(
            ForeignKey("user_books.id", ondelete="CASCADE"))
    tag_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tags.id", ondelete="CASCADE"))
    rating_value: Mapped[int | None] = mapped_column(Integer)

    # Relationships
    user_books: Mapped["UserBook"] = Relationship(back_populates="book_tags")
    tag: Mapped["Tag"] = Relationship(back_populates="book_tags")


    __table_args__: tuple[Any, ...] = (
            UniqueConstraint('user_book_id', 'tag_id', name='_user_book_tag_uc'),
            CheckConstraint('rating_value >= 0 AND rating_value <= 5', name="rating_between_0_and_5"),
            )

class EntryTag(Base):
    __tablename__: str = "entry_tags"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    entry_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("entries.id", ondelete="CASCADE"))
    tag_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tags.id", ondelete="CASCADE"))

    # Relationships
    entry: Mapped["Entry"] = Relationship(back_populates="entry_tags")
    tag: Mapped["Tag"] = Relationship(back_populates="entry_tags")

    __table_args__: tuple[Any, ...] = (
            UniqueConstraint('entry_id', 'tag_id', name='_user_entry_tag_uc'),
            )
