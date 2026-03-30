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
from user import User
from book import UserBook

class Base(DeclarativeBase):
    pass


class Journal(Base):
    __tablename__ = "journals"

    id: Mapped[Uuid] = mapped_column(primary_key=True)
    user_book_id: Mapped[int] = mapped_column(ForeignKey("user_books.id")) #journals belong to a book
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id")) # And a user
    content: Mapped[str] = mapped_column(String(500)) #Limit content to 500 characters
    date_made: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now()) 

    # Relationships
    user: Mapped["User"] = Relationship(back_populates="journals")
    user_book: Mapped["UserBook"] = Relationship(back_populates="journals")


