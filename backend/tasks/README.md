# Background Tasks

## Overview

This directory contains Celery task definitions for handling asynchronous operations in the AI Dashboard backend. Tasks are organized by domain and follow a consistent pattern of implementation with proper error handling and retry mechanisms.

## Directory Structure

```
tasks/
├── __init__.py
├── worker.py           # Celery worker configuration and utilities
├── analytics/         # Analytics generation tasks
│   └── generate_metrics.py
├── call/             # Call processing tasks
│   ├── call_processing.py
│   ├── process_call.py
│   └── task_definitions.py
├── campaign/         # Campaign management tasks
│   └── schedule_calls.py
├── lead/            # Lead management tasks
│   ├── process_lead.py
│   ├── qualification.py
│   └── task_definitions.py
└── utils/           # Utility tasks and helpers
    └── test_tasks.py
```

## Task Domains

### Analytics Tasks

- Metric generation
- Report creation
- Data aggregation

### Call Tasks

- Call processing
- Recording management
- Call status updates

### Campaign Tasks

- Campaign scheduling
- Call scheduling
- Campaign status updates

### Lead Tasks

- Lead updates
- Lead qualification
- Tag management
- Batch processing

## Task Configuration

### Default Settings

```python
TASK_DEFAULT_QUEUE = 'lead_queue'
TASK_DEFAULT_RETRY_DELAY = 5  # seconds
TASK_MAX_RETRIES = 3
```

### Queue Structure

Each domain has its dedicated queue:

- `analytics_tasks`
- `call_tasks`
- `campaign_tasks`
- `lead_tasks`
- `default`

## Worker Configuration

### Starting Workers

```bash
# Start worker for specific queue
python -m backend.tasks.worker lead_tasks 4

# Start worker with all queues
celery -A backend.celery_app worker -Q default,lead_tasks,call_tasks,analytics_tasks,campaign_tasks
```

### Worker Options

- `queue`: Queue name or comma-separated list
- `concurrency`: Number of worker processes
- `loglevel`: Logging level (INFO, DEBUG, etc.)

## Task Implementation Pattern

### Task Definition

```python
@app.task(
    name='domain.task_name',
    bind=True,
    max_retries=TASK_MAX_RETRIES,
    queue=TASK_DEFAULT_QUEUE
)
def task_function(self, *args, **kwargs):
    try:
        # Task implementation
        pass
    except Exception as e:
        # Retry with exponential backoff
        self.retry(exc=e, countdown=TASK_DEFAULT_RETRY_DELAY * (2 ** self.request.retries))
```

### Async Operation Pattern

```python
# Create event loop
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

try:
    # Define async operation
    async def _operation():
        async with get_db() as session:
            # Perform database operations
            pass

    # Run operation
    result = loop.run_until_complete(_operation())
    return result

finally:
    # Clean up
    loop.close()
```

## Error Handling

### Retry Mechanism

- Exponential backoff
- Maximum retry limit
- Retry delay configuration
- Error logging

### Error Types

1. Database Errors
2. External Service Errors
3. Validation Errors
4. Resource Not Found
5. Process Timeouts

## Testing

### Mock Repositories

The tasks package includes mock repositories for testing:

```python
class MockLeadRepository:
    """Mock repository for lead tasks."""
    async def get_lead_by_id(self, lead_id: str):
        pass

    async def update_lead(self, lead_id: str, lead_data: Dict[str, Any]):
        pass
```

### Running Tests

```bash
# Run task-specific tests
pytest tests/tasks/

# Run with coverage
pytest tests/tasks/ --cov=backend.tasks
```

## Development Guidelines

### 1. Creating New Tasks

1. Create task in appropriate domain directory
2. Follow established pattern:
   - Task decorator with proper configuration
   - Error handling and retries
   - Async operation support
   - Proper logging

### 2. Task Best Practices

- Use meaningful task names
- Implement proper retries
- Add comprehensive logging
- Include type hints
- Document parameters and returns
- Handle edge cases
- Use atomic operations

### 3. Queue Management

- Choose appropriate queue
- Set proper concurrency
- Configure time limits
- Monitor queue health
- Handle queue backlog

## Monitoring

### Logging

- Task start/completion
- Error conditions
- Retry attempts
- Performance metrics

### Metrics to Monitor

1. Task Success Rate
2. Processing Time
3. Queue Length
4. Retry Count
5. Error Rate

## Dependencies

- Celery: Task queue implementation
- Redis: Message broker
- SQLAlchemy: Database operations
- asyncio: Async operation support
- logging: Task logging
