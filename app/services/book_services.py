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
#region books
    #TODO One day work on a feature that will get a total number of results between database
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
#endregion
#region user books

    async def view_book(
            self, 
            user_id: uuid.UUID, 
            book_id: uuid.UUID) -> schemas.BookCover | schemas.UserBookCover:
        """
        The user clicks on a search result. They're taken to the cover of their book, or
        the generic version of the book's cover if not
        Args:
            user_id: The user
            book_id: The book being selected
        Returns: Either a BookCover or a UserBookCover

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
        Upserts a use book into the database
        Args:
            schema: A pydantic model containg a user id, a book id, and a shelf id, and a list of book tags

        Returns: A newly made or updated user book cover
            
        """
        async with self.uow:
                # 2. Save the UserBook
                user_book = await self.uow.books.save_user_book(book_schema=schema)
                # 5. Get Book
                book = await self.uow.books.get_book_with_id(user_book.book_id)
                if not book:
                    raise HTTPException(404, "Book not found")
                new_tags: list[schemas.BookTagDisplay] = []
                if schema.tags:
                    new_tags = await self.sync_book_tags(user_book_id=user_book.id, new_book_tags=schema.tags)

                new_book = schemas.UserBookCover(
                    user_book_id=user_book.id,
                    title=book.title,
                    thumbnail=book.meta_data.get("thumbnail"),
                    description=book.description,
                    authors=book.authors,
                    tags=new_tags
                )
                return new_book

    async def sync_book_tags(
            self, 
            user_book_id: uuid.UUID,
            new_book_tags: list[schemas.BookTagIngestSchema]) -> list[schemas.BookTagDisplay]:
        async with self.uow:
            if not new_book_tags:
                return []
            await self.uow.books.delete_book_tags(user_book_id=user_book_id)

            inserted_tags = await self.uow.books.upsert_book_tags(user_book_id=user_book_id, schemas=new_book_tags)
            return [
                    schemas.BookTagDisplay(
                        id=i.id,
                        name=i.name,
                        rating_value=i.rating_value
                        )
                    for i in inserted_tags
                    ]
#endregion
#region entries
    async def submit_entry(self, schema: schemas.EntryIngestSchema) -> schemas.EntryPublic:
        """
        Insert new tags, then use the returned tags alongside a returned entry from the database
        to create a schema that can be sent back to the user

        Args:
        schema: The EntryIngestionSchema containing the user book id, content,
        page, whether it's private, and a list of TagIngestionSchema

        Returns: A newly created Entry Schema
        """
        async with self.uow:
            row = await self.uow.books.create_book_entry(schema=schema)
            new_tags: list[schemas.EntryTag] = []
            if schema.tags:
                new_tags = await self.sync_entry_tags(new_tags=schema.tags)
            entry = schemas.EntryPublic(
                id=row.id,
                content=row.content,
                page=row.page,
                chapter=row.chapter,
                tags= new_tags
            )
            return entry 

    async def sync_entry_tags(self, new_tags: list[schemas.EntryTagIngestSchema]) -> list[schemas.EntryTag]:
            # Guard clause: If there's nothing to sync, don't bother the DB
            if not new_tags:
                return []
            async with self.uow:
                # 1. Clear existing tags
                await self.uow.entries.delete_entry_tags(entry_id=new_tags[0].entry_id)

                # 2. Build the Internal models
                entry_tags: list[schemas.EntryTag] = [
                    schemas.EntryTag(
                        entry_id=n.entry_id,
                        tag_id=n.tag_id,
                        name=n.name
                    )
                    for n in new_tags
                ]
                # 3. Save and return
                _ = await self.uow.entries.create_entry_tag(tags=entry_tags)
                return entry_tags

    async def get_entries_for_book(self, user_book_id: uuid.UUID, entry_type: str) -> list[schemas.EntryPublic] | None:
        """
        Get all the entries for a user's book
        Args:
            user_book_id: the user's book
            entry_type: The type of entry they're looking at

        Returns: A list of entries (notes, quotes, or journals)
            
        """
        async with self.uow:
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

    async def get_entries_with_params(self, search_params: schemas.EntrySearchSchema) -> list[schemas.EntryPublic]:
        async with self.uow:
            result = await self.uow.entries.get_entries_with_params(search_schema=search_params)
            entries: list[schemas.EntryPublic] = [
                    schemas.EntryPublic(
                        id=r.id,
                        content=r.content,
                        page=r.page,
                        chapter=r.chapter,
                        tags=None
                        )
                    for r in result
                    ]
            entry_tags: dict[uuid.UUID, list[schemas.EntryTag]] = await self.uow.entries.get_tags_for_entries(entries=entries)
            for e in entries:
                e.tags = entry_tags[e.id]
                pass
            return entries

    async def delete_entries(self, ids: list[uuid.UUID]) -> None:
        await self.uow.entries.delete_book_entries(entry_ids=ids)
#endregion

