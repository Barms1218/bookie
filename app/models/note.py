from typing import TYPE_CHECKING, List, Optional 
from sqlalchemy import ForeignKey, String, func, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column, Relationship
from .base import Base
import datetime
import uuid

if TYPE_CHECKING:
    from .user import User
    from .tag import Tag
class Note(Base):
    __tablename__ = "notes"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    # Foreign Keys
    user_book_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user_books.id"))
    trope_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tags.id"))
    
    content: Mapped[str] = mapped_column(Text)
    page_number: Mapped[Optional[int]] = mapped_column(Integer)
    # This is where your Tropes (Enemies-to-Lovers) live!
    note_type: Mapped[str] = mapped_column(String, default="general") 
    created_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())
    tags: Mapped[List["Tag"]] = Relationship(secondary="note_tags",back_populates="notes")

    user: Mapped["User"] = Relationship(back_populates="notes")


