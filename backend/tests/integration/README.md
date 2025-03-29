# Integration Tests

This directory contains integration tests that verify the functionality of the application with actual external dependencies.

## Celery Integration Tests

The Celery integration tests verify that:

1. Tasks can be properly submitted to Celery workers
2. Celery workers correctly execute the tasks
3. Results are properly returned and can be tracked
4. The service layer correctly offloads work to background tasks when requested

### Prerequisites

Before running these tests, make sure you have:

1. Redis server running
2. Database configured and accessible
3. Celery installed

### Running the Tests

To run the integration tests:

```bash
# From the project root
pytest backend/tests/integration/test_celery_integration.py -v --run-integration
```

The `--run-integration` flag is required to run integration tests, as they are skipped by default to speed up regular test runs.

### Specific Test Cases

- `test_update_lead_task_execution`: Tests the end-to-end update_lead task execution
- `test_update_lead_after_call_task_execution`: Tests updating a lead after a call
- `test_qualify_lead_task_execution`: Tests lead qualification tasks
- `test_add_tags_to_lead_task_execution`: Tests adding tags to a lead
- `test_service_background_task_offloading`: Tests the service layer's ability to offload tasks

### How It Works

The tests:

1. Start a Celery worker with specific configuration for testing
2. Create test data in the database
3. Submit tasks to the worker
4. Wait for task completion
5. Verify the expected changes were made
6. Clean up test data
7. Stop the Celery worker

### Troubleshooting

If the tests fail, check:

1. Redis server is running (`redis-cli ping` should return PONG)
2. Database is accessible
3. Celery worker is able to start (check for environment issues)
4. Timeouts are sufficient (adjust the timeout in `wait_for_task_completion` if needed) 