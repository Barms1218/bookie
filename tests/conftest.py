import pytest
from unittest.mock import AsyncMock
from app.dependencies import UnitOfWork
import app.schemas as schemas
import app.services as services

@pytest.fixture
def mock_uow():
    """Provides a mocked UnitOfWork for service testing."""
    uow = AsyncMock(spec=UnitOfWork)
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=False)
    # Ensure nested repositories are also mocked
    uow.books = AsyncMock()
    uow.tags = AsyncMock()
    uow.users = AsyncMock()
    return uow

@pytest.fixture
def book_service(mock_uow):
    mock_client = AsyncMock()
    return services.BookService(api_key="", client=mock_client, uow=mock_uow)
