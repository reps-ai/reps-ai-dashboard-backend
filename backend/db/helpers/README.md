# Database Helpers

This directory contains helper functions for database operations that are too complex to be included directly in the repository implementations.

## Purpose

The helpers in this directory serve several purposes:

1. **Separation of Concerns**: Keep repository implementations clean and focused on their interface
2. **Code Reuse**: Allow complex database operations to be reused across different repositories
3. **Maintainability**: Isolate complex queries in dedicated files for easier maintenance
4. **Testing**: Enable isolated testing of complex database operations

## Structure

The helpers are organized by domain:

- `lead/`: Helper functions for lead-related database operations
- `campaign/`: Helper functions for campaign-related database operations
- `call/`: Helper functions for call-related database operations
- `analytics/`: Helper functions for analytics-related database operations
- `gym/`: Helper functions for gym-related database operations
- `common/`: Helper functions that are used across multiple domains

## Usage

These helpers should be imported and used by repository implementations. They should not be used directly by services or tasks.

Example:

```python
# In a repository implementation
from ...helpers.lead.lead_queries import get_lead_with_related_data

async def get_lead_by_id(self, lead_id: str) -> Optional[Dict[str, Any]]:
    """Get lead details by ID."""
    return await get_lead_with_related_data(self.session, lead_id)
```

## Guidelines

1. Helper functions should focus on database operations only
2. They should not contain business logic
3. They should be stateless and rely only on the provided session
4. They should be well-documented with docstrings
5. They should handle database-specific error cases 