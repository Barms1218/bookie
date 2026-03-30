from datetime import time, timezone
from typing import List
from typing import Optional
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Uuid
from sqlalchemy import String, JSON, func, Integer, Float
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import Relationship
import datetime
from user import User


class Base(DeclarativeBase):
    pass


class BookClub(Base):
    __tablename__ = "book_clubs"

    id: Mapped[Uuid] = mapped_column(primary_key=True)
    invite_code: Mapped[str] = mapped_column(String, index=True, unique=True)
    current_book: Mapped[Optional[Uuid]] = mapped_column(ForeignKey("books.id"))
    favorite_book: Mapped[Uuid] = mapped_column(ForeignKey("books.id"))
    created_on: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    users: Mapped[List["User"]] = Relationship(secondary="club_members", back_populates="clubs")

class ClubMember(Base):
    __tablename__ = "club_members"

    id: Mapped[Uuid] = mapped_column(primary_key=True)
    user_id: Mapped[Uuid] = mapped_column(ForeignKey("users.id"))
    club_id: Mapped[Uuid] = mapped_column(ForeignKey("book_clubs.id"))
    role: Mapped[str] = mapped_column(String, default="member")
