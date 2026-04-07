import httpx
from sqlalchemy.sql.functions import user
from app.database.unit_of_work import UnitOfWork
import app.schemas as schemas
from fastapi import HTTPException
from pydantic import ValidationError
import uuid



class BookService:
    """

    Attributes: 
        api_key: 
        base_url: 
        client: 
        uow: 
    """
    def __init__(self, api_key: str, client: httpx.AsyncClient, uow: UnitOfWork):
        self.api_key: str = api_key
        self.base_url: str = "https://www.googleapis.com/books/v1/volumes"
        self.client: httpx.AsyncClient = client
        self.uow: UnitOfWork = uow 

    # One day work on a feature that will get a total number of results between database
    # And API
    async def get_book_with_term(self, term: str) -> list[schemas.BookSearchResult] | None:
        """

        Args:
            term: 

        Returns:
            

        Raises:
            HTTPException: 
        """
        valid_books = []
        async with self.uow:
                db_books = await self.uow.books.search_books_local(term) 
               
                if db_books:
                    return db_books
                params = {"q": term, "key": self.api_key}
                response = await self.client.get(self.base_url, params=params)
     
                if not response.is_success: 
                    raise HTTPException(status_code=502, detail="External API Failure")

                raw_data = response.json()

                # Google returns everything in one big items dictionary
                items = raw_data.get("items", [])

                for item in items:
                    volume_info = item.get("volumeInfo", {})
                    try:
                        book = schemas.BookIngestSchema(**volume_info)
                        saved_book = await self.uow.books.save_book_to_db(book)
                        valid_books.append(saved_book)
                    except ValidationError as e:
                        # If a book has bad data, ignore it and move on
                        print(f"Skipping book: {e}")
                        continue

                await self.uow.commit()

        return valid_books 

    async def view_book(
            self, 
            user_id: uuid.UUID, 
            book_id: uuid.UUID) -> schemas.BookCover | schemas.UserBookCover:
        """

        Args:
            user_id: 
            book_id: 

        Returns:
            

        Raises:
            HTTPException: 
        """
        async with self.uow:
            result = await self.uow.books.get_user_book(user_id=user_id, book_id=book_id)
            if result:
                    return schemas.UserBookCover(
                    user_book_id=result.user_book.id,
                    title=result.book.title,
                    thumbnail=result.book.meta_data.get("thumbnail"),
                    description=result.book.description,
                    authors=result.book.authors,
                    tags=result.book_tags
                    ) 

            book = await self.uow.books.get_book_with_id(id=book_id)
            if not book:
                raise HTTPException(404, "No Book Found")
            return schemas.BookCover(
                    book_id=book.id,
                    title=book.title,
                    thumbnail=book.meta_data.get("thumbnail"),
                    description=book.description,
                    categories=book.meta_data.get("categories"),
                    authors=book.authors,
                    total_pages=book.page_count
                    )

    async def save_user_book(self, schema: schemas.UserBookIngest) -> schemas.UserBookCover | None:
        """

        Args:
            schema: 

        Returns:
            
        """
        async with self.uow:
            # 1. Handle Tags
            tag_names = [t.name for t in schema.tags] if schema.tags else []
            tags_from_db = await self.uow.tags.get_or_create_tags(names=tag_names)
            
            # Create a lookup: {"History": UUID-123, "Fiction": UUID-456}
            tag_lookup = {t.id: t.name for t in tags_from_db}
        
            # 2. Save the UserBook
            user_book = await self.uow.books.save_user_book(book_schema=schema)
        
            # 3. Build the Upsert List
            # We loop over the schema.tags because that's where the 'rating_value' is!

        
            # 4. Perform the Upsert
            # Assuming your upsert function takes a list of schemas
            inserted_tags = await self.uow.books.upsert_book_tags(schemas=schema.tags)

            book_tags: list[schemas.BookTagDisplay] = [
                    schemas.BookTagDisplay(
                        id=t.id,
                        name=tag_lookup[t.id],
                        rating_value=t.rating_value

                        )
                    for t in inserted_tags
                    ]
        
            # 5. Get Book
            book = await self.uow.books.get_book_with_id(user_book.book_id)
            if not book:
                raise HTTPException(404, "Book not found")
          
            return schemas.UserBookCover(
                   user_book_id=user_book.id,
                   title=book.title,
                   thumbnail=book.meta_data.get("Thumbnail"),
                   description=book.description,
                   authors=book.authors,
                   tags=book_tags
                    )

    async def submit_entry(self, schema: schemas.EntryIngestSchema) -> schemas.EntryPublic:
        """
        Insert new tags, then use the returned tags alongside a returned entry from the database
        to create a schema that can be sent back to the user

        Args:
        schema: The EntryIngestionSchema containing the user book id, content,
        page, whether it's private, and a list of TagIngestionSchema

        Returns: A newly created Entry Schema
        """
        new_tags = []
        async with self.uow:
            try:
                new_tags = []
                if schema.tags:
                    names: list[str] = [t.name for t in schema.tags]         
                    new_tags = await self.uow.tags.get_or_create_tags(names=names)
                row = await self.uow.books.create_book_entry(schema=schema)
                entry = schemas.EntryPublic(
                    id=row.id,
                    content=row.content,
                    page=row.page,
                    chapter=row.chapter,
                    tags=[
                        schemas.EntryTag(
                            entry_id=row.id,
                            tag_id=t.id,
                            name=t.name
                            )
                        for t in new_tags
                        ]
                    )
            except:
                self.uow.rollback
                raise HTTPException(500, "Failed to insert book entry")

            return entry 

    async def get_entries_for_book(self, user_book_id: uuid.UUID, entry_type: str) -> list[schemas.EntryPublic] | None:
        entries = await self.uow.entries.get_book_entries(user_book_id=user_book_id, type=entry_type)
        entry_schemas: list[schemas.EntryPublic] = [
                schemas.EntryPublic(
                    id=e.id,
                    content=e.content,
                    page=e.page,
                    chapter=e.chapter,
                    tags=[
                        schemas.EntryTag(
                            entry_id=e.id,
                            tag_id=t.id,
                            name=t.name
                            )
                        for t in e.tags
                        ]
                    )
                    for e in entries
                ]

        return entry_schemas
