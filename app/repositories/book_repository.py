from typing import Optional, List
from sqlalchemy import select, or_, func
from sqlalchemy.dialects.postgresql import insert
from app.schemas.book import BookIngestSchema
from app.models.book import Book
from sqlalchemy.ext.asyncio import AsyncSession
import uuid


class BookRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def search_books_local(self, term: str) -> List[Book]:
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
        return list(result.scalars().all()) # Extract the Book models from the rows

    # Upsert function. If there's a conflict on the isbn update the title
    async def save_book_to_db(self, book_schema: BookIngestSchema):
        # Prepare the insert
        cleaned_data = book_schema.model_dump(by_alias=True)
        stmt = insert(Book).values(**cleaned_data)

        upsert_stmt = stmt.on_conflict_do_update(
                index_elements=['isbn'],
                set_={
                    "title": stmt.excluded.title,
                    "authors": stmt.excluded.authors,
                    "meta_data": stmt.excluded.meta_data,
                    "page_count": stmt.excluded.page_count
                    }
                ).returning(Book)
        
        result = await self.db.execute(upsert_stmt)
        return result.scalar_one()

    async def get_book_by_isbn(self, isbn: str) -> Optional[Book]:
        stmt = select(Book).where(Book.isbn == isbn)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_book_with_id(self, id: uuid.UUID) ->: Optional[Book]:
        stmt = select(Book).where(Book.id == id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_books(self) -> List[Book]:
        stmt = (
                select(Book)
                ).limit(20)

        result = await self.db.execute(stmt)
        return list(result.scalars().all())
