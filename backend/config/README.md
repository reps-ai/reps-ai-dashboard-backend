# Configuration Management

## Overview

This directory contains configuration settings for the AI Dashboard backend. It manages various aspects of the application including environment variables, API settings, task queue configuration, and system-wide constants.

## Files

```
config/
├── __init__.py
├── settings.py      # Application settings and constants
└── celery_config.py # Celery task queue configuration
```

## Application Settings (settings.py)

### Environment Settings

```python
ENV = os.getenv("ENV", "development")
DEBUG = ENV == "development"
```

### Categories of Settings

1. **External API Configuration**

   - Retell API settings
   - AI service settings

2. **Campaign Settings**

   - Max calls per day
   - Call duration limits
   - Retry configurations

3. **Task Queue Settings**

   - Redis connection URLs
   - Queue configuration

4. **Logging Configuration**
   - Log levels
   - Log format settings

### Key Mappings

1. **Call Days**

   - Maps days to numerical values (0-6)
   - Used for scheduling and filtering

2. **Lead Qualification**

   - Hot (3)
   - Neutral (2)
   - Cold (1)

3. **Call Outcomes**

   - Appointment booked
   - Follow-up needed
   - Not interested
   - etc.

4. **Sentiment Analysis**
   - Positive
   - Neutral
   - Negative

## Celery Configuration (celery_config.py)

### Broker Settings

```python
broker_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
result_backend = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
```

### Task Queues

Dedicated queues for different task types:

- `default`: Default queue
- `lead_tasks`: Lead management tasks
- `call_tasks`: Call processing tasks
- `analytics_tasks`: Analytics generation
- `campaign_tasks`: Campaign management

### Task Routes

Routes tasks to appropriate queues:

```python
task_routes = {
    'backend.tasks.lead.*': {'queue': 'lead_tasks', 'routing_key': 'lead.tasks'},
    'backend.tasks.call.*': {'queue': 'call_tasks', 'routing_key': 'call.tasks'},
    'backend.tasks.analytics.*': {'queue': 'analytics_tasks', 'routing_key': 'analytics.tasks'},
    'backend.tasks.campaign.*': {'queue': 'campaign_tasks', 'routing_key': 'campaign.tasks'},
}
```

### Task Execution Settings

1. **Time Limits**

   - Task time limit: 1 hour
   - Soft time limit: 45 minutes

2. **Worker Settings**

   - Late acknowledgment
   - Prefetch multiplier
   - Task rejection on worker lost

3. **Retry Settings**
   - Max retries: 3
   - Retry intervals
   - Backoff strategy

## Environment Variables

### Required Variables

```bash
# Environment
ENV=development|staging|production

# Database
DATABASE_URL=postgresql+asyncpg://user:password@host:port/database

# Redis (Task Queue)
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# External APIs
RETELL_API_KEY=your_retell_api_key
AI_SERVICE_API_KEY=your_ai_service_key
```

### Optional Variables

```bash
# Campaign Settings
DEFAULT_MAX_CALLS_PER_DAY=50
DEFAULT_MAX_CALL_DURATION=300
DEFAULT_RETRY_NUMBER=2
DEFAULT_RETRY_GAP=1

# Logging
LOG_LEVEL=INFO
LOG_FORMAT="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

## Usage

### Loading Settings

```python
from backend.config.settings import (
    RETELL_API_KEY,
    DEFAULT_MAX_CALL_DURATION,
    LEAD_QUALIFICATION_MAPPING
)

# Use settings
max_duration = DEFAULT_MAX_CALL_DURATION
qualification_value = LEAD_QUALIFICATION_MAPPING["hot"]
```

### Celery Worker Configuration

Start a worker for specific queues:

```bash
celery -A backend.celery_app worker -Q lead_tasks,call_tasks
```

Start a worker for all queues:

```bash
celery -A backend.celery_app worker -Q default,lead_tasks,call_tasks,analytics_tasks,campaign_tasks
```

## Best Practices

1. **Environment Variables**

   - Use environment variables for sensitive data
   - Provide default values for development
   - Document all required variables

2. **Configuration Management**

   - Keep configurations modular
   - Use type hints for clarity
   - Document all settings
   - Use constants for repeated values

3. **Queue Management**

   - Separate queues by domain
   - Configure appropriate time limits
   - Implement retry strategies
   - Monitor queue health

4. **Security**
   - Never commit sensitive data
   - Use secure methods for API keys
   - Validate environment variables
   - Implement proper error handling

## Development Guidelines

1. **Adding New Settings**

   - Add to appropriate section
   - Include type hints
   - Add default values
   - Update documentation

2. **Modifying Existing Settings**

   - Ensure backward compatibility
   - Update all affected components
   - Update documentation
   - Test thoroughly

3. **Queue Management**
   - Follow naming conventions
   - Configure appropriate routes
   - Set proper time limits
   - Document queue purpose
