from typing import Annotated
from app.dependencies import get_book_service, get_current_user
from fastapi import APIRouter, Depends, HTTPException 
from app.services.book_services import BookService
import uuid
import app.schemas as schemas

router = APIRouter(prefix="/books", tags=["books"])

credentials_exception = HTTPException(
        status_code=401,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )

@router.get("/search/{user_id", 
            response_model=list[schemas.BookSearchResult],
            status_code=200)
async def search_books(
                term: str,
                service: Annotated[BookService, Depends(get_book_service)],
                current_user: Annotated[schemas.CurrentUser, Depends(get_current_user)]):
    return await service.get_book_with_term(id=current_user.id, term=term)


@router.post("/view/{book_id}/{user_id}", status_code=200)
async def select_listed_book(
        book_id: uuid.UUID, 
        service: Annotated[BookService, Depends(get_book_service)],
        current_user: Annotated[schemas.CurrentUser, Depends(get_current_user)]) -> schemas.UserBookCover | schemas.BookCover:
    return await service.view_book(user_id=current_user.id, book_id=book_id)

@router.post("/add", response_model=schemas.BookCover, status_code=201)
async def add_user_book(
        schema: schemas.UserBookIngest, 
        service: Annotated[BookService, Depends(get_book_service)],
        _: Annotated[schemas.CurrentUser, Depends(get_current_user)]):
    return await service.save_user_book(schema=schema)


@router.post("/entries/{user_book_id}", response_model=schemas.EntryPublic, status_code=201)
async def new_note(schema: schemas.EntryIngestSchema, service: Annotated[BookService, Depends(get_book_service)]):
   return await service.submit_entry(schema=schema) 

@router.post("/user_books/{user_book_id}/entries/{type}", response_model=list[schemas.EntryPublic], status_code=200)
async def get_book_entries(
                user_book_id: uuid.UUID, 
                type: str,
                service: Annotated[BookService, Depends(get_book_service)],
                _: Annotated[schemas.CurrentUser, Depends(get_current_user)]):
        return await service.get_entries_for_book(user_book_id=user_book_id, entry_type=type)


@router.delete("/entries/delete", status_code=200)
async def delete_book_entries(
        ids: list[uuid.UUID],
        service: Annotated[BookService, Depends(get_book_service)],
        _: Annotated[schemas.CurrentUser, Depends(get_current_user)]):
    return service.delete_entries(ids=ids)
