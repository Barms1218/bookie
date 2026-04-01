import pytest
from unittest.mock import AsyncMock
from app.dependencies import UnitOfWork
from app.services.journal_service import JournalService

pytest.fixture
def mock_uow():
    """Provides a mocked UnitOfWork for service testing."""
    uow = AsyncMock(spec=UnitOfWork)
    # Ensure nested repositories are also mocked
    uow.books = AsyncMock()
    uow.journals = AsyncMock()
    uow.quotes = AsyncMock()
    return uow

@pytest.fixture
def journal_service(mock_uow):
    """Provides a JournalService pre-configured with a mock UOW."""
    mock_client = AsyncMock()
    return JournalService(client=mock_client, uow=mock_uow)
