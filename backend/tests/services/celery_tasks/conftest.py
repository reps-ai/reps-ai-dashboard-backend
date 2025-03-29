"""
Pytest fixtures for Celery task testing.
"""
import pytest
from unittest.mock import MagicMock, patch
from typing import Dict, Any

# Example lead data for testing
@pytest.fixture
def lead_data() -> Dict[str, Any]:
    """Fixture providing test lead data."""
    return {
        "id": "0295e732-ccbe-4c37-99bc-8dc1fee34205",
        "first_name": "John",
        "last_name": "Smith",
        "email": "test@example.com",
        "lead_status": "open",
        "qualification_score": 1,
        "notes": "Test lead notes",
        "source": "website"
    }

# Example call data for testing
@pytest.fixture
def call_data() -> Dict[str, Any]:
    """Fixture providing test call data."""
    return {
        "call_id": "0e6164f3-1447-40cf-b311-ce042428253a",
        "duration": 120,
        "notes": "Test call notes",
        "outcome": "interested",
        "call_status": "completed",
        "qualification": 1
    }

# Mocked database session
@pytest.fixture
def mock_db_session():
    """Fixture providing a mocked database session."""
    session = MagicMock()
    return session

# Mocked context manager for get_db
@pytest.fixture
def mock_db_context(mock_db_session):
    """Fixture providing a mocked database context manager."""
    context = MagicMock()
    context.__aenter__.return_value = mock_db_session
    return context

# Patch for get_db
@pytest.fixture
def patch_get_db(mock_db_context):
    """Fixture providing a patch for get_db."""
    with patch('backend.tasks.lead.task_definitions.get_db', return_value=mock_db_context) as mock:
        yield mock

# Mocked repository
@pytest.fixture
def mock_repository():
    """Fixture providing a mocked lead repository."""
    repo = MagicMock()
    return repo

# Mocked service
@pytest.fixture
def mock_service():
    """Fixture providing a mocked lead service."""
    service = MagicMock()
    return service

# Patch for PostgresLeadRepository
@pytest.fixture
def patch_repository(mock_repository):
    """Fixture providing a patch for PostgresLeadRepository."""
    with patch('backend.tasks.lead.task_definitions.PostgresLeadRepository', return_value=mock_repository) as mock:
        yield mock

# Patch for DefaultLeadService
@pytest.fixture
def patch_service(mock_service):
    """Fixture providing a patch for DefaultLeadService."""
    with patch('backend.tasks.lead.task_definitions.DefaultLeadService', return_value=mock_service) as mock:
        yield mock 