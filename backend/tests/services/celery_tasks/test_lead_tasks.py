"""
Tests for lead background tasks.

This file contains all tests for lead-related Celery background tasks.
"""
import asyncio
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
from typing import Dict, Any

from backend.tasks.lead.task_definitions import (
    update_lead,
    update_lead_after_call,
    qualify_lead,
    add_tags_to_lead,
    update_lead_batch,
    MockLeadRepository
)

# Test data
TEST_LEAD_ID = "0295e732-ccbe-4c37-99bc-8dc1fee34205"
TEST_LEAD_DATA = {
    "first_name": "John",
    "last_name": "Smith",
    "email": "test@example.com",
    "lead_status": "open",
    "qualification_score": 1
}
TEST_CALL_DATA = {
    "call_id": "0e6164f3-1447-40cf-b311-ce042428253a",
    "duration": 120,
    "notes": "Test call notes",
    "outcome": "interested"
}
TEST_TAGS = ["test-tag-1", "test-tag-2"]

# Mock repository for testing
class TestMockLeadRepository:
    """Tests for the MockLeadRepository class used in task testing."""

    def test_get_lead_by_id(self):
        """Test the get_lead_by_id method."""
        # Arrange
        repo = MockLeadRepository(TEST_LEAD_ID, TEST_LEAD_DATA)
        
        # Act & Assert - Matching ID
        result = asyncio.run(repo.get_lead_by_id(TEST_LEAD_ID))
        assert result["id"] == TEST_LEAD_ID
        assert result["first_name"] == TEST_LEAD_DATA["first_name"]
        
        # Act & Assert - Non-matching ID
        non_matching_repo = MockLeadRepository("different-id", TEST_LEAD_DATA)
        result = asyncio.run(non_matching_repo.get_lead_by_id(TEST_LEAD_ID))
        assert result is None
    
    def test_update_lead(self):
        """Test the update_lead method."""
        # Arrange
        repo = MockLeadRepository(TEST_LEAD_ID, TEST_LEAD_DATA)
        
        # Act
        update_data = {"notes": "Updated notes"}
        result = asyncio.run(repo.update_lead(TEST_LEAD_ID, update_data))
        
        # Assert
        assert result["id"] == TEST_LEAD_ID
        assert result["notes"] == "Updated notes"
        assert "updated_at" in result
    
    def test_update_lead_after_call(self):
        """Test the update_lead_after_call method."""
        # Arrange
        repo = MockLeadRepository(TEST_LEAD_ID, TEST_LEAD_DATA)
        
        # Act
        result = asyncio.run(repo.update_lead_after_call(TEST_LEAD_ID, TEST_CALL_DATA))
        
        # Assert
        assert result["id"] == TEST_LEAD_ID
        assert result["call_data"] == TEST_CALL_DATA
        assert "updated_at" in result
    
    def test_update_lead_qualification(self):
        """Test the update_lead_qualification method."""
        # Arrange
        repo = MockLeadRepository(TEST_LEAD_ID, TEST_LEAD_DATA)
        
        # Act
        qualification = 1  # hot
        result = asyncio.run(repo.update_lead_qualification(TEST_LEAD_ID, qualification))
        
        # Assert
        assert result["id"] == TEST_LEAD_ID
        assert result["qualification"] == qualification
        assert "updated_at" in result
    
    def test_add_tags_to_lead(self):
        """Test the add_tags_to_lead method."""
        # Arrange
        repo = MockLeadRepository(TEST_LEAD_ID, TEST_LEAD_DATA)
        
        # Act
        result = asyncio.run(repo.add_tags_to_lead(TEST_LEAD_ID, TEST_TAGS))
        
        # Assert
        assert result["id"] == TEST_LEAD_ID
        assert result["tags"] == TEST_TAGS
        assert "updated_at" in result

# Task tests with mocked repository
@patch('backend.tasks.lead.task_definitions.PostgresLeadRepository')
@patch('backend.tasks.lead.task_definitions.DefaultLeadService')
@patch('backend.tasks.lead.task_definitions.get_db')
class TestLeadTasks:
    """Tests for lead task functionality."""
    
    def test_update_lead(self, mock_get_db, mock_service_class, mock_repo_class):
        """Test the update_lead task."""
        # Arrange
        mock_repo = MagicMock()
        mock_service = MagicMock()
        
        mock_repo_class.return_value = mock_repo
        mock_service_class.return_value = mock_service
        
        # Create a mock context manager for the database session
        mock_session = MagicMock()
        mock_context = MagicMock()
        mock_context.__aenter__.return_value = mock_session
        mock_get_db.return_value = mock_context
        
        # Configure the service's update_lead method to return a result
        mock_result = {"id": TEST_LEAD_ID, "status": "updated"}
        mock_service.update_lead.return_value = mock_result
        
        # Act
        result = update_lead(TEST_LEAD_ID, TEST_LEAD_DATA)
        
        # Assert
        assert result == mock_result
        mock_service.update_lead.assert_called_once_with(TEST_LEAD_ID, TEST_LEAD_DATA)
    
    def test_update_lead_after_call(self, mock_get_db, mock_service_class, mock_repo_class):
        """Test the update_lead_after_call task."""
        # Arrange
        mock_repo = MagicMock()
        mock_service = MagicMock()
        
        mock_repo_class.return_value = mock_repo
        mock_service_class.return_value = mock_service
        
        # Create a mock context manager for the database session
        mock_session = MagicMock()
        mock_context = MagicMock()
        mock_context.__aenter__.return_value = mock_session
        mock_get_db.return_value = mock_context
        
        # Configure the service's update_lead_after_call method to return a result
        mock_result = {"id": TEST_LEAD_ID, "status": "updated_after_call"}
        mock_service.update_lead_after_call.return_value = mock_result
        
        # Act
        result = update_lead_after_call(TEST_LEAD_ID, TEST_CALL_DATA)
        
        # Assert
        assert result == mock_result
        mock_service.update_lead_after_call.assert_called_once_with(TEST_LEAD_ID, TEST_CALL_DATA)
    
    def test_qualify_lead(self, mock_get_db, mock_service_class, mock_repo_class):
        """Test the qualify_lead task."""
        # Arrange
        mock_repo = MagicMock()
        mock_service = MagicMock()
        
        mock_repo_class.return_value = mock_repo
        mock_service_class.return_value = mock_service
        
        # Create a mock context manager for the database session
        mock_session = MagicMock()
        mock_context = MagicMock()
        mock_context.__aenter__.return_value = mock_session
        mock_get_db.return_value = mock_context
        
        # Configure the service's qualify_lead method to return a result
        mock_result = {"id": TEST_LEAD_ID, "qualification": 1}
        mock_service.qualify_lead.return_value = mock_result
        
        # Act
        result = qualify_lead(TEST_LEAD_ID, 1)
        
        # Assert
        assert result == mock_result
        mock_service.qualify_lead.assert_called_once_with(TEST_LEAD_ID, 1)
    
    def test_add_tags_to_lead(self, mock_get_db, mock_service_class, mock_repo_class):
        """Test the add_tags_to_lead task."""
        # Arrange
        mock_repo = MagicMock()
        mock_service = MagicMock()
        
        mock_repo_class.return_value = mock_repo
        mock_service_class.return_value = mock_service
        
        # Create a mock context manager for the database session
        mock_session = MagicMock()
        mock_context = MagicMock()
        mock_context.__aenter__.return_value = mock_session
        mock_get_db.return_value = mock_context
        
        # Configure the service's add_tags_to_lead method to return a result
        mock_result = {"id": TEST_LEAD_ID, "tags": TEST_TAGS}
        mock_service.add_tags_to_lead.return_value = mock_result
        
        # Act
        result = add_tags_to_lead(TEST_LEAD_ID, TEST_TAGS)
        
        # Assert
        assert result == mock_result
        mock_service.add_tags_to_lead.assert_called_once_with(TEST_LEAD_ID, TEST_TAGS)
    
    def test_update_lead_batch(self, mock_get_db, mock_service_class, mock_repo_class):
        """Test the update_lead_batch task."""
        # Arrange
        mock_repo = MagicMock()
        mock_service = MagicMock()
        
        mock_repo_class.return_value = mock_repo
        mock_service_class.return_value = mock_service
        
        # Create a mock context manager for the database session
        mock_session = MagicMock()
        mock_context = MagicMock()
        mock_context.__aenter__.return_value = mock_session
        mock_get_db.return_value = mock_context
        
        # Configure the service's update_lead method to return a result
        async def mock_update_lead(lead_id, data):
            return {"id": lead_id, "status": "updated"}
        
        mock_service.update_lead.side_effect = mock_update_lead
        
        # Act
        lead_ids = [TEST_LEAD_ID, "another-lead-id"]
        result = update_lead_batch(lead_ids, TEST_LEAD_DATA)
        
        # Assert
        assert result["successful"] == lead_ids
        assert len(result["failed"]) == 0
        assert mock_service.update_lead.call_count == 2 