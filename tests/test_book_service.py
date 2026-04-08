import pytest
import pytest_asyncio
import uuid
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException

from app.services import BookService 
import app.schemas as schemas


@pytest.mark.asyncio
async def test_book_tag_sync_success(book_service, mock_uow):
    user_book_id = uuid.uuid4()
    tag_id = uuid.uuid4()

    new_book_tags = [
            schemas.BookTagIngestSchema(name="Fantasy", rating_value=4)
            ]

    mock_tag = MagicMock()
    mock_tag.id = tag_id
    mock_tag.name = new_book_tags[0].name

    mock_book_tag = MagicMock()
    mock_book_tag.id = uuid.uuid4()
    mock_book_tag.name = "Fantasy"
    mock_book_tag.rating = 4

    mock_uow.books.delete_book_tags = AsyncMock()
    mock_uow.tags.get_or_create_tags = AsyncMock(return_value=[mock_tag])
    mock_uow.books.upsert_book_tags = AsyncMock(return_value=[mock_book_tag])

    result = await book_service.sync_book_tags(
            user_book_id=user_book_id,
            new_book_tags=new_book_tags
            )

    mock_uow.books.delete_book_tags.assert_awaited_once_with(user_book_id=user_book_id)
    mock_uow.tags.get_or_create_tags.assert_awaited_once_with(names=["Fantasy"])
    mock_uow.books.upsert_book_tags.assert_awaited_once()
    assert len(result) == 1
    assert result[0].name == "Fantasy"

@pytest.mark.asyncio
async def test_submit_entry_success(book_service, mock_uow):
    mock_row = MagicMock()
    mock_row.id = uuid.uuid4()
    mock_row.content = "Testing with a fixture!"
    mock_row.page_number = 15
    result = mock_uow.books.create_book_entry.return_value = mock_row
    await mock_uow.commit()
    assert result is not None
    mock_uow.commit.assert_awaited_once()
