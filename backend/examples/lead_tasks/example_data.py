"""
Example data for lead tasks.

This module provides example data structures for testing and demonstrating 
lead-related background tasks.
"""
from typing import Dict, Any, List

# Example lead ID for testing
EXAMPLE_LEAD_ID = "15603c96-8d3a-49a9-9a0d-aca2189d04f9" #Nathaniel	Guerra

# Example lead data for testing
EXAMPLE_LEAD_DATA: Dict[str, Any] = {
    "first_name": "Lewis",
    "last_name": "Hamilton",
    "email": "test@example.com",
    "lead_status": "open",
    "notes": "Test lead notes",
    "source": "website"
}

# Example call data for testing
EXAMPLE_CALL_DATA: Dict[str, Any] = {
    "call_id": "464b7377-559f-41f9-8c8d-79c7ad737a8b",
    "duration": 120,
    "notes": "Test call notes",
    "outcome": "interested",
    "call_status": "completed",
    "qualification": 1
}

# Example tags for testing
EXAMPLE_TAGS: List[str] = ["test-tag-1", "test-tag-2"]

# Example lead batch for testing
EXAMPLE_LEAD_BATCH: List[str] = [
    "0295e732-ccbe-4c37-99bc-8dc1fee34205",
    "17ea3ea3-56fc-4e8c-b264-6764207f318c",
    "216b3ef7-faad-4d7a-8e7a-28d9c99ca42e"
]

# Example batch update data
EXAMPLE_BATCH_UPDATE_DATA: Dict[str, Any] = {
    "lead_status": "contacted",
    "notes": "Batch updated via background task"
} 