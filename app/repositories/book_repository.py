from sqlalchemy import select, or_, func, update
from sqlalchemy.dialects.postgresql import insert
from app.schemas.book import BookIngestSchema, BookSearchResult, DetailedBook, UserBookIngest 
from app.database.models import Book, UserBook
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import uuid



class BookRepository:
    def __init__(self, db: AsyncSession):
        self.db: AsyncSession = db

    async def search_books_local(self, term: str) -> list[BookSearchResult]:
        search_term = f"%{term}%"
        stmt = (
                select(Book)
                .where(
                    or_(
                        # 1. Case-insensitive Title search
                        Book.title.ilike(search_term),
                    
                        # 2. Check if the Authors list (Postgres Array) contains the term
                        # This is faster than a string search for lists
                        func.array_to_string(Book.authors, ' ').ilike(search_term), 
                    
                        # 3. Reach into the JSONB 'extra_metadata' to search the description
                        # ->> extracts as text so we can use .ilike()
                        Book.meta_data["description"].astext.ilike(search_term)
                    )
                )
                .limit(20) # Good practice to avoid dumping 10k rows into memory
        )
        result = await self.db.execute(stmt) # Get the rows object from sql
        
        search_results = list(result.scalars().all()) # Extract the Book models from the rows
        
        # List comprehension to turn all the search results into something the user will want to see.
        # They can get more information when looking at the books in-depth in their library.
        books: list[BookSearchResult] = [
                BookSearchResult(id=s.id,
                                 thumbnail=s.meta_data.get("small_thumbnail"),
                                 title=s.title,
                                 authors=s.authors)
                for s in search_results
                ]

        return books
        

    # Upsert function. If there's a conflict on the isbn update the title
    async def save_book_to_db(self, book_schema: BookIngestSchema):
        # Prepare the insert
        data = book_schema.model_dump()

        print(data)
        stmt = insert(Book).values(**data)
        upsert_stmt = stmt.on_conflict_do_update(
                index_elements=['isbn'],
                set_={
                    Book.title: stmt.excluded.title,
                    Book.page_count: stmt.excluded.page_count,
                    Book.meta_data: stmt.excluded.meta_data
                    }
                ).returning(Book)
        result = await self.db.execute(upsert_stmt)
        return result.scalar_one()

    async def save_user_book(self, book_schema: UserBookIngest):
        uploaded_book = book_schema.model_dump()

        
        stmt = insert(UserBook).values(**uploaded_book)
        upsert_stmt = stmt.on_conflict_do_update(
                index_elements=['book_id', 'user_id'],
                set_={
                    UserBook.added_at: func.now(),
                    UserBook.reading_status: func.coalesce(stmt.excluded.reading_status, UserBook.reading_status),
                    UserBook.current_page: func.coalesce(stmt.excluded.current_page, UserBook.current_page),
                    UserBook.rating: func.coalesce(stmt.excluded.rating, UserBook.rating)
                    }
                ).returning(UserBook)

        result = await self.db.execute(upsert_stmt)
        await self.db.commit()
        row = result.scalar_one()
        return row


    async def get_user_books(self, user_id: uuid.UUID) -> list[BookSearchResult]:
        stmt = (
            select(
                UserBook.book_id.label("id"),
                Book.title,
                Book.authors,
                # Pull the thumbnail out of JSONB and label it exactly as the schema expects
                Book.meta_data["small_thumbnail"].astext.label("thumbnail") 
            )
            .join(Book, UserBook.book_id == Book.id)
            .where(UserBook.user_id == user_id, UserBook.deleted_at.is_(None))
        )

        result = await self.db.execute(stmt)
        
        # 1. Use .mappings() so each row looks like a dict
        # 2. Use .all() because we have multiple columns (NOT .scalars())
        rows = result.mappings().all()

        # 3. Manually create the SearchResult list
        return [
            BookSearchResult(
                id=row["id"],
                thumbnail=row["thumbnail"],
                title=row["title"],
                authors=row["authors"]
            )
            for row in rows
        ]

    async def get_user_book(self, book_id: uuid.UUID, user_id: uuid.UUID) -> DetailedBook:
        stmt = (
            select(UserBook, Book)
            .join(Book, UserBook.book_id == Book.id)
            .where(UserBook.book_id == book_id)
            .where(UserBook.user_id == user_id) # Security: Ensure this book belongs to THIS user
            )

        result = await self.db.execute(stmt)
        user_book, book = result.one()

        return DetailedBook(
                book_id=book.id,
                title=book.title,
                thumbnail=book.meta_data["thumbnail"],
                description=book.meta_data["description"],
                categories=book.meta_data["categories"],
                authors=book.authors,
                total_pages=book.page_count,
                rating=user_book.rating_value
                )


    async def get_book_by_isbn(self, isbn: str) -> Book | None:
        stmt = select(Book).where(Book.isbn == isbn)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_book_with_id(self, id: uuid.UUID) -> Book | None:
        stmt = select(Book).where(Book.id == id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_books(self) -> list[Book]:
        stmt = (
                select(Book)
                ).limit(20)

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def delete_book(self, book_id: uuid.UUID) -> datetime:
        stmt = (update(UserBook)
        .where(UserBook.id == book_id)
        .values(deleted_at =func.now())
        )

        result = await self.db.execute(stmt)
        return result.scalar_one()
