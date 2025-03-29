"""
Celery application configuration.
"""
from celery import Celery
import os

# Create Celery app
app = Celery('backend')

# Load configuration from config module
app.config_from_object('backend.config.celery_config')

# Auto-discover tasks from registered task modules
app.autodiscover_tasks([
    'backend.tasks.lead',
    'backend.tasks.call',
    'backend.tasks.campaign',
    'backend.tasks.analytics',
    'backend.tasks.utils.test_tasks'
])

if __name__ == '__main__':
    app.start() 