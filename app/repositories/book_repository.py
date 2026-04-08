from sqlalchemy import Row, select, or_, func, update, delete
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import contains_eager, selectinload 
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from typing import Any
import uuid
import app.schemas as schemas
import app.database.models as models

class BookRepository:
    def __init__(self, db: AsyncSession):
        self.db: AsyncSession = db

    async def search_books_local(self, term: str) -> list[schemas.BookSearchResult]:
        search_term = f"%{term}%"
        stmt = (
                select(models.Book)
                .where(
                    or_(
                        # 1. Case-insensitive Title search
                        models.Book.title.ilike(search_term),
                    
                        # 2. Check if the Authors list (Postgres Array) contains the term
                        # This is faster than a string search for lists
                        models.Book.authors.contains([search_term]), 
                    
                        models.Book.ts_vector.match(search_term),
                    )
                )
                .where(models.Book.title.not_ilike("%Box Set%"))
                .where(models.Book.title.not_ilike("%Full Series%"))
                        
                .limit(20) # Good practice to avoid dumping 10k rows into memory
        )
        result = await self.db.execute(stmt) # Get the rows object from sql
        
        search_results = list(result.scalars().all()) # Extract the Book models from the rows
        
        # List comprehension to turn all the search results into something the user will want to see.
        # They can get more information when looking at the books in-depth in their library.
        books: list[schemas.BookSearchResult] = [
                schemas.BookSearchResult(id=s.id,
                                 thumbnail=s.meta_data.get("small_thumbnail"),
                                 title=s.title,
                                 authors=s.authors)
                for s in search_results
                ]

        return books
        

    # Upsert function. If there's a conflict on the isbn update the title
    async def save_book_to_db(self, book_schema: schemas.BookIngestSchema) -> models.Book:
        # Prepare the insert
        data = book_schema.model_dump()

        print(data)
        stmt = insert(models.Book).values(**data)
        upsert_stmt = stmt.on_conflict_do_update(
                index_elements=['isbn'],
                set_={
                    models.Book.title: stmt.excluded.title,
                    models.Book.page_count: stmt.excluded.page_count,
                    models.Book.meta_data: stmt.excluded.meta_data
                    }
                ).returning(models.Book)
        result = await self.db.execute(upsert_stmt)
        return result.scalar_one()

    async def save_user_book(self, book_schema: schemas.UserBookIngest) -> models.UserBook:
        uploaded_book = book_schema.model_dump(exclude={'tags'})

        stmt = insert(models.UserBook).values(**uploaded_book)
        upsert_stmt = stmt.on_conflict_do_update(
                index_elements=['book_id', 'user_id'],
                set_={
                    models.UserBook.shelf_id: func.coalesce
                    (stmt.excluded.shelf_id, models.UserBook.shelf_id),
                    models.UserBook.reading_status: func.coalesce(
                        stmt.excluded.reading_status, models.UserBook.reading_status),
                    }
                ).returning(models.UserBook)

        result = await self.db.execute(upsert_stmt)
        await self.db.commit()
        row = result.scalar_one()
        return row


    async def get_user_books(self, user_id: uuid.UUID) -> Row[tuple[uuid.UUID, str, list[str], Any]] | None:
        stmt = (
            select(
                models.UserBook.book_id.label("id"),
                models.Book.title,
                models.Book.authors,
                # Pull the thumbnail out of JSONB and label it exactly as the schema expects
                models.Book.meta_data["small_thumbnail"].astext.label("thumbnail") 
            )
            .join(models.Book, models.UserBook.book_id == models.Book.id)
            .where(models.UserBook.user_id == user_id, models.UserBook.deleted_at.is_(None))
        )

        result = await self.db.execute(stmt)
        
        # 1. Use .mappings() so each row looks like a dict
        # 2. Use .all() because we have multiple columns (NOT .scalars())
        #rows = result.mappings().all()
        rows = result.one_or_none()
        return rows

    # Need to accept a schema to update the book, probably just a UserBookUpdateSchema
    async def get_user_book(
            self,
            user_id: uuid.UUID,
            book_id: uuid.UUID) -> Row[tuple[models.UserBook]] | None:
        stmt = (
                select(models.UserBook)
                .join(models.Book, models.UserBook.book_id == book_id)
                .where(models.UserBook.user_id == user_id, models.UserBook.book_id == book_id)
                .options(
                    contains_eager(models.UserBook.book),
                    selectinload(models.UserBook.book_tags)
                    )
                )    
        result = await self.db.execute(stmt)
        return result.one_or_none()

    async def get_book_by_isbn(self, isbn: str) -> models.Book | None:
        stmt = select(models.Book).where(models.Book.isbn == isbn)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_book_with_id(self, id: uuid.UUID) -> models.Book | None:
        stmt = select(models.Book).where(models.Book.id == id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_books(self) -> list[models.Book]:
        stmt = (
                select(models.Book)
                ).limit(20)

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def delete_book(self, book_id: uuid.UUID) -> datetime:
        stmt = (update(models.UserBook)
        .where(models.UserBook.id == book_id)
        .values(deleted_at =func.now())
        )

        result = await self.db.execute(stmt)
        return result.scalar_one()

    async def upsert_book_tags(
            self,
            user_book_id: uuid.UUID,
            schemas: list[schemas.BookTag]):
        payload = [
                {
                    "user_book_id": s.user_book_id,
                    "tag_id": s.tag_id,
                    "rating_value": s.rating_value
                    }
                for s in schemas
                ]
        stmt = insert(models.BookTag).values(payload)

        upsert_stmt = stmt.on_conflict_do_update(
                index_elements=['user_book_id', 'tag_id'],
                set_={
                    "rating_value": stmt.excluded.rating_value
                    }
                )

        result = await self.db.execute(upsert_stmt)

        return await self.get_book_tags_with_name(user_book_id=user_book_id) 

    async def get_book_tags_with_name(self, user_book_id: uuid.UUID):
        stmt = (select(models.BookTag.id, models.Tag.name, models.BookTag.rating_value)
                .join(models.Tag, models.BookTag.tag_id == models.Tag.id)
                .where(models.BookTag.user_book_id == user_book_id)
                )

        result = await self.db.execute(stmt)

        return list(result.all())

    async def create_book_entry(self, schema: schemas.EntryIngestSchema):
        """

        Args:
            schemas: 

        Returns:
            
        """
        stmt = insert(models.Entry).values(**schema.model_dump(exclude={"tags"}))

        upsert_stmt = stmt.on_conflict_do_update(
                index_elements=['user_book_id','created_on'],
                set_={
                    models.Entry.content: stmt.excluded.content,
                    models.Entry.page: stmt.excluded.page,
                    models.Entry.updated_on: func.now(),
                    models.Entry.is_private: stmt.excluded.is_private
                    }
                ).returning(models.Entry)

        result = await self.db.execute(upsert_stmt)

        return result.scalar_one()

    async def get_book_entries(self, user_book_id: uuid.UUID):
        pass

    async def delete_book_tags(self, user_book_id) ->  None:
        stmt = (delete(models.BookTag)
                .where(models.BookTag.user_book_id == user_book_id))

        result = await self.db.execute(stmt)

        return result.scalar_one_or_none()
