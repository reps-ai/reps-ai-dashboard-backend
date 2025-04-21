"""
Celery application configuration.
"""
from celery import Celery
import os
from celery.schedules import crontab

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

# Add campaign scheduling task routes
app.conf.task_routes = {
    'campaign.schedule_campaign': {'queue': 'campaign_tasks'},
    'call.trigger_call': {'queue': 'campaign_tasks'},
    'campaign.schedule_all_campaigns': {'queue': 'campaign_tasks'}
}

# Configure Celery beat schedule
app.conf.beat_schedule = {
    'schedule-all-campaigns-daily': {
        'task': 'campaign.schedule_all_campaigns',
        'schedule': crontab(hour=6, minute=0),  # Runs daily at 6:00 AM UTC
        'args': (),
    }
}

if __name__ == '__main__':
    app.start()