"""
Test suite for the DefaultCallService class.
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch, call
from uuid import UUID
import json
from pprint import pprint

# Mock the retell module
import sys
from unittest.mock import MagicMock
sys.modules['retell'] = MagicMock()

from backend.services.call.implementation import DefaultCallService
from backend.db.repositories.call.interface import CallRepository
from backend.integrations.retell.interface import RetellIntegration

# Test data constants
TEST_LEAD_ID = "00848ea2-6d44-4a52-a552-fc6a26306a4a"
TEST_CAMPAIGN_ID = "a2b87087-4a35-4be5-8919-b0937e6b4eac"
TEST_BRANCH_ID = "632bfb51-70a4-4679-845d-4e399b4ec395"
TEST_GYM_ID = "0072ba23-9c82-4dfe-8edf-05279a0ecdc9"
TEST_CALL_ID = "26aaab03-7521-4d79-b7b6-cf375cc57595"

@pytest.fixture
def mock_call_repository():
    """Create a mock CallRepository."""
    repository = AsyncMock(spec=CallRepository)
    return repository

@pytest.fixture
def mock_retell_integration():
    """Create a mock RetellIntegration."""
    integration = AsyncMock(spec=RetellIntegration)
    return integration

@pytest.fixture
def call_service(mock_call_repository, mock_retell_integration):
    """Create a DefaultCallService instance with mocked dependencies."""
    return DefaultCallService(
        call_repository=mock_call_repository,
        retell_integration=mock_retell_integration
    )

@pytest.mark.asyncio
async def test_get_call(call_service, mock_call_repository):
    """Test getting a call by ID."""
    print("\n=== Testing get_call ===")
    
    # Mock repository response
    mock_data = {
        "id": TEST_CALL_ID,
        "lead_id": TEST_LEAD_ID,
        "gym_id": TEST_GYM_ID,
        "branch_id": TEST_BRANCH_ID,
        "call_status": "completed",
        "call_type": "outbound",
        "created_at": datetime.now(),
        "start_time": datetime.now(),
        "end_time": datetime.now(),
        "duration": 300
    }
    mock_call_repository.get_call_by_id.return_value = mock_data
    
    print("\nMocked Data:")
    pprint(mock_data)
    
    # Call the service
    result = await call_service.get_call(TEST_CALL_ID)
    
    print("\nActual Result:")
    pprint(result)
    
    # Verify repository call
    mock_call_repository.get_call_by_id.assert_called_once_with(TEST_CALL_ID)
    
    # Verify result
    assert result["id"] == TEST_CALL_ID
    assert result["lead_id"] == TEST_LEAD_ID
    assert result["call_status"] == "completed"

@pytest.mark.asyncio
async def test_get_calls_by_campaign(call_service, mock_call_repository):
    """Test getting calls by campaign."""
    print("\n=== Testing get_calls_by_campaign ===")
    
    # Mock repository response
    mock_data = {
        "calls": [
            {
                "id": TEST_CALL_ID,
                "lead_id": TEST_LEAD_ID,
                "campaign_id": TEST_CAMPAIGN_ID,
                "call_status": "completed",
                "created_at": datetime.now()
            }
        ],
        "pagination": {
            "total": 1,
            "page": 1,
            "page_size": 50,
            "pages": 1
        }
    }
    mock_call_repository.get_calls_by_campaign.return_value = mock_data
    
    print("\nMocked Data:")
    pprint(mock_data)
    
    # Call the service
    result = await call_service.get_calls_by_campaign(TEST_CAMPAIGN_ID)
    
    print("\nActual Result:")
    pprint(result)
    
    # Verify repository call
    assert mock_call_repository.get_calls_by_campaign.call_args == call(TEST_CAMPAIGN_ID, 1, 50)
    
    # Verify result
    assert len(result) == 1
    assert result[0]["id"] == TEST_CALL_ID
    assert result[0]["campaign_id"] == TEST_CAMPAIGN_ID

@pytest.mark.asyncio
async def test_get_calls_by_lead(call_service, mock_call_repository):
    """Test getting calls by lead."""
    print("\n=== Testing get_calls_by_lead ===")
    
    # Mock repository response
    mock_data = {
        "calls": [
            {
                "id": TEST_CALL_ID,
                "lead_id": TEST_LEAD_ID,
                "call_status": "completed",
                "created_at": datetime.now()
            }
        ],
        "pagination": {
            "total": 1,
            "page": 1,
            "page_size": 50,
            "pages": 1
        }
    }
    mock_call_repository.get_calls_by_lead.return_value = mock_data
    
    print("\nMocked Data:")
    pprint(mock_data)
    
    # Call the service
    result = await call_service.get_calls_by_lead(TEST_LEAD_ID)
    
    print("\nActual Result:")
    pprint(result)
    
    # Verify repository call
    assert mock_call_repository.get_calls_by_lead.call_args == call(TEST_LEAD_ID, 1, 50)
    
    # Verify result
    assert len(result) == 1
    assert result[0]["id"] == TEST_CALL_ID
    assert result[0]["lead_id"] == TEST_LEAD_ID

@pytest.mark.asyncio
async def test_get_calls_by_date_range(call_service, mock_call_repository):
    """Test getting calls by date range."""
    print("\n=== Testing get_calls_by_date_range ===")
    
    # Prepare test data
    start_date = datetime.now() - timedelta(days=7)
    end_date = datetime.now()
    
    # Mock repository response
    mock_data = {
        "calls": [
            {
                "id": TEST_CALL_ID,
                "lead_id": TEST_LEAD_ID,
                "gym_id": TEST_GYM_ID,
                "call_status": "completed",
                "created_at": datetime.now()
            }
        ],
        "pagination": {
            "total": 1,
            "page": 1,
            "page_size": 50,
            "pages": 1
        }
    }
    mock_call_repository.get_calls_by_date_range.return_value = mock_data
    
    print("\nMocked Data:")
    pprint(mock_data)
    
    # Call the service
    result = await call_service.get_calls_by_date_range(
        gym_id=TEST_GYM_ID,
        start_date=start_date,
        end_date=end_date
    )
    
    print("\nActual Result:")
    pprint(result)
    
    print("\nDate Range:")
    print(f"Start Date: {start_date}")
    print(f"End Date: {end_date}")
    
    # Verify repository call
    assert mock_call_repository.get_calls_by_date_range.call_args == call(TEST_GYM_ID, start_date, end_date, 1, 50)
    
    # Verify result
    assert len(result) == 1
    assert result[0]["id"] == TEST_CALL_ID
    assert result[0]["gym_id"] == TEST_GYM_ID 