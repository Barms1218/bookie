import httpx
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

    async def save_user_book(self, schema: schemas.UserBookIngest):
        """

        Args:
            schema: 

        Returns:
            
        """
        return await self.uow.books.save_user_book(book_schema=schema)

    async def change_reading_status(self, schema: schemas.ReadingStatusUpdateSchema) -> str | None:
            """

            Args:
                schema: A schema holding an id to a user book and the new reading status

            Returns: The new reading status
                

            Raises:
                HTTPException: If the sql update failed
            """
            updated_status = await self.uow.books.change_reading_status(schema=schema)
            if not updated_status:
                raise HTTPException(404, "No user book found")

            return updated_status


    async def submit_entry(self, schema: schemas.EntryIngestSchema) -> schemas.EntryPublic:
        """
        Creates an entry along with any tags the user attaches during creation

        Args:
        schema: The EntryIngestionSchema containing the user book id, content,
        page, whether it's private, and a list of TagIngestionSchema

        Returns: A newly created Entry Schema
        """
        new_tags = []
        async with self.uow:
            row = await self.uow.books.create_book_entry(schema=schema)
            entry = schemas.EntryPublic(
                id=row.id,
                content=row.content,
                page=row.page_number if row.page_number else 0
                )
            
            new_tags = []
            if schema.tags:
                names: list[str] = [t.name for t in schema.tags]              
                new_tags = await self.uow.tags.get_or_create_tags(names=names)
                
            tag_lookup = {t.name: t.id for t in new_tags }
            entry_tags: list[schemas.EntryTagIngestSchema] = [
                    schemas.EntryTagIngestSchema(
                        entry_id=entry.id,
                        tag_id=tag_lookup[t.name],
                        name=t.name
                        )
                    for t in new_tags
                    ] 

            _ = await self.uow.entries.create_entry_tag(tags=entry_tags) 

            entry.tags = [schemas.EntryTag(entry_tag_id=t.tag_id, name=t.name) for t in entry_tags]

        return entry 
