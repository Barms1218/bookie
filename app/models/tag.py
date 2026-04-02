from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import String, Float
from sqlalchemy.orm import Mapped, mapped_column, Relationship
from .base import Base
import uuid

if TYPE_CHECKING:
    from .note import Note
    from .user_book import UserBook

class Tag(Base):
    __tablename__ = "tropes"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    genre: Mapped[str]
    rating: Mapped[Optional[float]] = mapped_column(Float)
    meta_data: Mapped[dict]

    # Relationships
    notes: Mapped[List["Note"]] = Relationship(secondary="note_tags", back_populates="tags")    
    user_books: Mapped[List["UserBook"]] = Relationship(secondary="book_tags", back_populates="tags")


