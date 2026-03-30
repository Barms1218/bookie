from datetime import time, timezone
from typing import List
from typing import Optional
from sqlalchemy import DateTime, ForeignKey, Uuid
from sqlalchemy import String, func 
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import Relationship
import datetime
from journal import Journal
from book import UserBook 
from book_clubs import BookClub

class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[Uuid] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True)

    date_joined: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now()) 

    # Relationships
    user_books: Mapped[List["UserBook"]] = Relationship(back_populates="user")
    journals: Mapped[List["Journal"]] = Relationship(back_populates="users")
    clubs: Mapped[List["BookClub"]] = Relationship(secondary="club_members", back_populates="user")                                             

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.name!r})"


