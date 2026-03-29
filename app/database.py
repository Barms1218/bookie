from typing import List
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy import String, JSON, Float
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import Relationship

class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(30))

class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    isbn: Mapped[str] = mapped_column(JSON)
    title: Mapped[str] = mapped_column(String(30))
    authors: Mapped[List[str]] = mapped_column(JSON)
    page_count: Mapped[int] = mapped_column(JSON)


class UserBook(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"))
    
    pass

class Journals(Base):
    __tablename__ = "journals"

    id: Mapped[int] = mapped_column(primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("book.id")) #journals belong to a book
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id")) # And a user
    content: Mapped[str] = mapped_column(String(500)) #Limit content to 500 characters

