from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import DateTime, ForeignKey, Uuid, String, func
from sqlalchemy.orm import Mapped, mapped_column, Relationship
from .base import Base
import datetime
import uuid


if TYPE_CHECKING:
    from .user import User

class BookClub(Base):
    __tablename__ = "book_clubs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    invite_code: Mapped[str] = mapped_column(String, index=True, unique=True)
    current_book: Mapped[Optional[Uuid]] = mapped_column(ForeignKey("books.id"))
    favorite_book: Mapped[Uuid] = mapped_column(ForeignKey("books.id"))
    created_on: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    users: Mapped[List["User"]] = Relationship(secondary="club_members", back_populates="clubs")

class ClubMember(Base):
    __tablename__ = "club_members"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[Uuid] = mapped_column(ForeignKey("users.id"))
    club_id: Mapped[Uuid] = mapped_column(ForeignKey("book_clubs.id"))
    role: Mapped[str] = mapped_column(String, default="member")
