import pytest
from unittest.mock import AsyncMock
from app.services.journal_service import JournalService
from app.schemas.journal import JournalIngestSchema
from fastapi import HTTPException
import uuid

@pytest.mark.asyncio
async def test_submit_journal_success(journal_service, mock_uow):
    # 1. Setup the mock behavior
    mock_uow.books.get_book_with_id.return_value = AsyncMock(title="The Hobbit")
    
    # 2. Run the logic
    test_payload = JournalIngestSchema(
        userID=uuid.uuid4(),
        bookID=uuid.uuid4(),
        content="Testing with a fixture!"
    )
    result = await journal_service.submit_journal(test_payload)

    # 3. Assert
    assert result.book_title == "The Hobbit"
    mock_uow.commit.assert_awaited_once()

@pytest.mark.asyncio
async def test_submit_journal_book_not_found():
    mock_uow = AsyncMock()
    # Simulate the DB returning None (book not found)
    mock_uow.books.get_book_with_id.return_value = None
    
    service = JournalService(client=AsyncMock(), uow=mock_uow)
    
    test_payload = JournalIngestSchema(
        userID=uuid.uuid4(),
        bookID=uuid.uuid4(),
        content="This should fail"
    )

    # We EXPECT an HTTPException with a 404 status
    with pytest.raises(HTTPException) as exc:
        await service.submit_journal(test_payload)
    
    assert exc.value.status_code == 404
