from typing import TYPE_CHECKING, Optional
from sqlalchemy import ForeignKey, Float 
from sqlalchemy.orm import Mapped, mapped_column, Relationship
from .base import Base
import uuid

if TYPE_CHECKING:
    from .user_book import UserBook
    from .tag import Tag

class BookTag(Base):
    __tablename__ = "book_tags"

    user_book_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user_books.id"), primary_key=True)
    tag_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tags.id"), primary_key=True)

    # Relationships
    user_books: Mapped["UserBook"] = Relationship(back_populates="book_tags")
    tag: Mapped["Tag"] = Relationship(back_populates="book_links")

class NoteTag(Base):
    __tablename__ = "note_tags"

    note_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("notes.id"), primary_key=True)
    tag_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tags.id"), primary_key=True)
    rating_value: Mapped[Optional[float]] = mapped_column(Float)

