"""
Example data for lead tasks.

This module provides example data structures for testing and demonstrating 
lead-related background tasks.
"""
from typing import Dict, Any, List

# Example lead ID for testing
EXAMPLE_LEAD_ID = "0295e732-ccbe-4c37-99bc-8dc1fee34205"

# Example lead data for testing
EXAMPLE_LEAD_DATA: Dict[str, Any] = {
    "first_name": "John",
    "last_name": "Smith",
    "email": "test@example.com",
    "lead_status": "open",
    "qualification_score": 1,
    "notes": "Test lead notes",
    "source": "website"
}

# Example call data for testing
EXAMPLE_CALL_DATA: Dict[str, Any] = {
    "call_id": "0e6164f3-1447-40cf-b311-ce042428253a",
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
    "1395e732-ddbe-5d48-88cd-9ed2gff45316",
    "2495f843-eecf-6e59-77de-0fe3hgg56427"
]

# Example batch update data
EXAMPLE_BATCH_UPDATE_DATA: Dict[str, Any] = {
    "lead_status": "contacted",
    "notes": "Batch updated via background task"
} 