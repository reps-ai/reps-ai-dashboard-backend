"""
Test the call-related background tasks.
"""
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from uuid import uuid4

from ...tasks.call.task_definitions import process_retell_call
from ...db.repositories.call.implementations import PostgresCallRepository

# Mock data
MOCK_CALL_ID = str(uuid4())
MOCK_RETELL_DATA = {
    "start_timestamp": int(datetime.now().timestamp() * 1000),
    "end_timestamp": int(datetime.now().timestamp() * 1000) + 60000,
    "recording_url": "https://example.com/recording.wav",
    "transcript": "Test transcript",
    "call_analysis": {
        "call_summary": "Test summary",
        "user_sentiment": "positive"
    }
}

@pytest.fixture
def mock_session():
    """Create a mock database session."""
    session = MagicMock()
    session.commit = MagicMock()
    session.rollback = MagicMock()
    session.close = MagicMock()
    return session

@pytest.fixture
def mock_session_local(mock_session):
    """Mock the SessionLocal to return our mock session."""
    with patch('backend.db.connections.database.SessionLocal', return_value=mock_session):
        yield

@patch.object(PostgresCallRepository, 'update_call')
def test_process_retell_call_success(mock_update_call, mock_session_local):
    """Test successful processing of Retell call data."""
    
    # Setup mock
    mock_update_call.return_value = {
        "id": MOCK_CALL_ID,
        "call_status": "completed"
    }
    
    # Run task
    result = process_retell_call(MOCK_CALL_ID, MOCK_RETELL_DATA)
    
    # Verify call repository was used correctly
    mock_update_call.assert_called_once()
    update_data = mock_update_call.call_args[0][1]
    
    # Verify data mapping
    assert update_data["call_status"] == "completed"
    assert update_data["recording_url"] == MOCK_RETELL_DATA["recording_url"]
    assert update_data["transcript"] == MOCK_RETELL_DATA["transcript"]
    assert update_data["summary"] == MOCK_RETELL_DATA["call_analysis"]["call_summary"]
    assert update_data["sentiment"] == MOCK_RETELL_DATA["call_analysis"]["user_sentiment"].lower()
    
    # Verify task result
    assert result is True

@patch.object(PostgresCallRepository, 'update_call')
def test_process_retell_call_failure(mock_update_call, mock_session_local, mock_session):
    """Test handling of update failure in background task."""
    
    # Setup mock to return None (indicating failure)
    mock_update_call.return_value = None
    
    # Run task
    result = process_retell_call(MOCK_CALL_ID, MOCK_RETELL_DATA)
    
    # Verify behavior
    assert result is False
    mock_session.rollback.assert_not_called()  # No need to rollback for None result
    mock_session.close.assert_called_once()

@patch.object(PostgresCallRepository, 'update_call')
def test_process_retell_call_exception(mock_update_call, mock_session_local, mock_session):
    """Test handling of exceptions in background task."""
    
    # Setup mock to raise an exception
    mock_update_call.side_effect = Exception("Test error")
    
    # Run task and verify exception handling
    with pytest.raises(Exception):
        process_retell_call(MOCK_CALL_ID, MOCK_RETELL_DATA)
    
    # Verify proper cleanup
    mock_session.rollback.assert_called_once()
    mock_session.close.assert_called_once()
