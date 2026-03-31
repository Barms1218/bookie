from typing import Optional, List
from sqlalchemy import select, or_, func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.sql.compiler import ilike_case_insensitive
from app.schemas.book import BookIngestSchema
from app.models.book import Book
from sqlalchemy.ext.asyncio import AsyncSession

async def search_books_local(db: AsyncSession, term: str) -> List[Book]:
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

    result = await db.execute(stmt) # Get the rows object from sql
    return list(result.scalars().all()) # Extract the Book models from the rows

# Upsert function. If there's a conflict on the isbn update the title
async def save_book_to_db(db: AsyncSession, book_schema: BookIngestSchema):
    # Prepare the insert
    stmt = insert(Book).values(
        isbn=book_schema.isbn,
        title=book_schema.title,
        authors=book_schema.authors,
        meta_data=book_schema.metadata.model_dump()
    ).on_conflict_do_update(
        index_elements=['isbn'],
        set_={"title": book_schema.title}
    ).returning(Book) # Vital to showing what was inserted
    
    result = await db.execute(stmt)
    await db.commit() # This pushes the data to Postgres
    return result.scalar_one()

async def get_book_by_isbn(db: AsyncSession, isbn: str) -> Optional[Book]:
    stmt = select(Book).where(Book.isbn == isbn)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
