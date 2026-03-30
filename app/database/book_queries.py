from sqlalchemy import select, or_
from app.schemas import tables
from sqlalchemy.ext.asyncio import AsyncSession

async def search_books_local(db: AsyncSession, term: str):
    search_term = f"%{term}%"

    stmt = select(tables.Book).where(
            or_(
                tables.Book.title.ilike(search_term),
                tables.Book.authors.contains([term]) # Checks if the list contains the name
            )
        )

    result = await db.execute(stmt)
    return result.scalars().all()
