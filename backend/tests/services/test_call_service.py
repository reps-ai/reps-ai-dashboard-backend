"""
Test the call service with background task processing.
"""
from datetime import datetime
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from ...services.call.implementation import DefaultCallService
from ...integrations.retell.interface import RetellIntegration
from ...db.repositories.call import CallRepository

# Mock data
MOCK_LEAD_ID = str(uuid4())
MOCK_GYM_ID = str(uuid4())
MOCK_BRANCH_ID = str(uuid4())
MOCK_CALL_ID = str(uuid4())
MOCK_EXTERNAL_CALL_ID = "mock_retell_call_id"

MOCK_RETELL_RESPONSE = {
    "status": "registered",
    "call_id": MOCK_EXTERNAL_CALL_ID,
    "start_timestamp": int(datetime.now().timestamp() * 1000),
    "end_timestamp": int(datetime.now().timestamp() * 1000) + 60000,  # 1 minute later
    "recording_url": "https://example.com/recording.wav",
    "transcript": "This is a mock transcript",
    "call_analysis": {
        "call_summary": "Mock call summary",
        "user_sentiment": "positive"
    }
}

@pytest.fixture
def mock_call_repository():
    repo = AsyncMock(spec=CallRepository)
    
    async def mock_create_call(call_data):
        return {
            "id": MOCK_CALL_ID,
            "lead_id": call_data["lead_id"],
            "gym_id": call_data["gym_id"],
            "branch_id": call_data["branch_id"],
            "call_status": call_data["call_status"],
            "created_at": call_data["created_at"]
        }
    
    async def mock_update_call(call_id, update_data):
        return {
            "id": call_id,
            **update_data
        }
    
    repo.create_call.side_effect = mock_create_call
    repo.update_call.side_effect = mock_update_call
    return repo

@pytest.fixture
def mock_retell_integration():
    integration = AsyncMock(spec=RetellIntegration)
    
    async def mock_create_call(*args, **kwargs):
        return MOCK_RETELL_RESPONSE
    
    integration.create_call.side_effect = mock_create_call
    return integration

@pytest.mark.asyncio
@patch('backend.tasks.call.task_definitions.process_retell_call')
async def test_trigger_call_with_background_task(mock_process_retell_call, mock_call_repository, mock_retell_integration):
    """Test the complete flow of triggering a call with background task."""
    
    # Initialize service with mocks
    service = DefaultCallService(
        call_repository=mock_call_repository,
        retell_integration=mock_retell_integration
    )
    
    # Mock data
    lead_data = {
        "id": MOCK_LEAD_ID,
        "phone_number": "+1234567890",
        "name": "Test User",
        "gym_id": MOCK_GYM_ID,
        "branch_id": MOCK_BRANCH_ID,
        "interest": "test_interest"
    }
    
    # Trigger call
    result = await service.trigger_call(
        lead_id=MOCK_LEAD_ID,
        lead_data=lead_data
    )
    
    # Verify initial call creation
    mock_call_repository.create_call.assert_called_once()
    created_call_data = mock_call_repository.create_call.call_args[0][0]
    assert created_call_data["lead_id"] == MOCK_LEAD_ID
    assert created_call_data["call_status"] == "scheduled"
    
    # Verify Retell integration called
    mock_retell_integration.create_call.assert_called_once_with(
        lead_data=lead_data,
        campaign_id=None,
        max_duration=None
    )
    
    # Verify call status update
    mock_call_repository.update_call.assert_called_once()
    update_data = mock_call_repository.update_call.call_args[0][1]
    assert update_data["call_status"] == "in_progress"
    assert update_data["external_call_id"] == MOCK_EXTERNAL_CALL_ID
    
    # Verify background task queued
    mock_process_retell_call.delay.assert_called_once_with(
        MOCK_CALL_ID,
        MOCK_RETELL_RESPONSE
    )
    
    # Verify final result
    assert result["id"] == MOCK_CALL_ID
    assert result["call_status"] == "in_progress"

@pytest.mark.asyncio
async def test_trigger_call_retell_error(mock_call_repository, mock_retell_integration):
    """Test handling of Retell error response."""
    
    # Modify Retell mock to return error
    error_response = {
        "status": "error",
        "message": "Mock error message"
    }
    mock_retell_integration.create_call.side_effect = AsyncMock(return_value=error_response)
    
    service = DefaultCallService(
        call_repository=mock_call_repository,
        retell_integration=mock_retell_integration
    )
    
    # Trigger call
    result = await service.trigger_call(
        lead_id=MOCK_LEAD_ID,
        lead_data={
            "id": MOCK_LEAD_ID,
            "phone_number": "+1234567890",
            "name": "Test User",
            "gym_id": MOCK_GYM_ID,
            "branch_id": MOCK_BRANCH_ID,
            "interest": "test_interest"
        }
    )
    
    # Verify error handling
    assert result["call_status"] == "error"
    mock_process_retell_call.delay.assert_not_called()

@pytest.mark.asyncio
async def test_trigger_call_unexpected_status(mock_call_repository, mock_retell_integration):
    """Test handling of unexpected Retell status."""
    
    # Modify Retell mock to return unexpected status
    unexpected_response = {
        "status": "unknown_status",
        "call_id": MOCK_EXTERNAL_CALL_ID
    }
    mock_retell_integration.create_call.side_effect = AsyncMock(return_value=unexpected_response)
    
    service = DefaultCallService(
        call_repository=mock_call_repository,
        retell_integration=mock_retell_integration
    )
    
    # Trigger call
    result = await service.trigger_call(
        lead_id=MOCK_LEAD_ID,
        lead_data={
            "id": MOCK_LEAD_ID,
            "phone_number": "+1234567890",
            "name": "Test User",
            "gym_id": MOCK_GYM_ID,
            "branch_id": MOCK_BRANCH_ID,
            "interest": "test_interest"
        }
    )
    
    # Verify error handling
    assert result["call_status"] == "error"
    assert "human_notes" in result
    assert "unexpected status" in result["human_notes"]
    mock_process_retell_call.delay.assert_not_called()
