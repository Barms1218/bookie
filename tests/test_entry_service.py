import pytest
import pytest_asyncio
import uuid
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException

from app.services.entry_service import EntryService
from app.schemas.entry_schemas import EntryIngestSchema


@pytest_asyncio.fixture
async def mock_uow():
    uow = AsyncMock()
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=False)
    return uow


@pytest_asyncio.fixture
async def entry_service(mock_uow):
    return EntryService(client=AsyncMock(), uow=mock_uow)


@pytest.mark.asyncio
async def test_submit_entry_success(entry_service, mock_uow):
    mock_row = MagicMock()
    mock_row.id = uuid.uuid4()
    mock_row.content = "Testing with a fixture!"
    mock_row.page_number = 15
    result = mock_uow.entries.create_entry.return_value = mock_row
    await mock_uow.commit()
    assert result is not None
    mock_uow.commit.assert_awaited_once()


