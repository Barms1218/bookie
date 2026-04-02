from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import ForeignKey, String, Text, Integer, ARRAY, Index
from sqlalchemy.orm import Mapped, mapped_column, Relationship
from .base import Base
import uuid

if TYPE_CHECKING:
    from .user import User
    from .user_book import UserBook

class Quote(Base):
    __tablename__ = "quotes"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_book_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user_books.id")) #journals belong to a book
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id")) 
    characters: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)
    content: Mapped[str] = mapped_column(Text)
    page: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Relationships
    user: Mapped["User"] = Relationship(back_populates="quotes")
    user_book: Mapped["UserBook"] = Relationship(back_populates="quotes")



# Indexes
Index("ix_quotes_characters_gin", Quote.characters, postgresql_using="gin")
