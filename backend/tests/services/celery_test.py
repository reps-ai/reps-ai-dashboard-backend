"""
Tests for Celery tasks integration.
"""
import asyncio
import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock

from backend.tasks.utils.test_tasks import add_numbers, log_message
from backend.services.lead.factory import create_lead_service

@pytest.mark.asyncio
async def test_simple_tasks():
    """Test simple Celery tasks with mocking."""
    
    # Mock the delay method to avoid actual task execution during tests
    with patch('backend.tasks.utils.test_tasks.add_numbers.delay') as mock_add_delay, \
         patch('backend.tasks.utils.test_tasks.log_message.delay') as mock_log_delay:
         
        # Setup mock return values
        mock_task = MagicMock()
        mock_task.id = "mock-task-id"
        mock_add_delay.return_value = mock_task
        mock_log_delay.return_value = mock_task
        
        # Call the tasks
        task1 = add_numbers.delay(5, 7)
        task2 = log_message.delay("Test message")
        
        # Verify tasks were called with correct arguments
        mock_add_delay.assert_called_once_with(5, 7)
        mock_log_delay.assert_called_once_with("Test message")
        
        # Verify task IDs are accessible
        assert task1.id == "mock-task-id"
        assert task2.id == "mock-task-id"

@pytest.mark.asyncio
async def test_lead_service_background_tasks():
    """Test lead service with background tasks."""
    
    # Mock the lead repository to avoid database operations
    with patch('backend.db.repositories.lead.LeadRepository') as MockLeadRepo, \
         patch('backend.tasks.lead.task_definitions.update_lead.delay') as mock_update_task:
         
        # Setup mock lead repository
        mock_repo = MagicMock()
        MockLeadRepo.return_value = mock_repo
        
        # Setup mock task
        mock_task = MagicMock()
        mock_task.id = "mock-lead-task-id"
        mock_update_task.return_value = mock_task
        
        # Create lead service with mocked repository
        lead_service = create_lead_service()
        
        # Test data
        test_lead_id = "test-lead-123"
        lead_data = {
            "name": "Test Background Lead",
            "email": "test@example.com",
            "updated_at": datetime.now().isoformat(),
            "use_background_task": True
        }
        
        # Call service method with background flag
        result = await lead_service.update_lead(test_lead_id, lead_data)
        
        # Verify background task was queued
        assert result["status"] == "update_queued"
        
        # Verify the task was called with correct parameters
        # Note: use_background_task should be removed before passing to the task
        expected_data = lead_data.copy()
        expected_data.pop("use_background_task")
        mock_update_task.assert_called_once_with(test_lead_id, expected_data)

if __name__ == '__main__':
    # This enables running as a standalone script for quick tests
    asyncio.run(pytest.main(['-xvs', __file__])) 