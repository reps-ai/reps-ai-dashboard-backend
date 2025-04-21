"""
Celery configuration settings.
"""
import os
from kombu import Queue, Exchange

# Broker settings (Redis)
broker_url = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
result_backend = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/0")

# Serialization settings
task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']

# Task execution settings
task_acks_late = True
worker_prefetch_multiplier = 1
task_reject_on_worker_lost = True

# Task time limits
task_time_limit = 60 * 60  # 1 hour
task_soft_time_limit = 45 * 60  # 45 minutes

# Task queues
task_default_queue = 'default'
task_queues = (
    Queue('default', Exchange('default'), routing_key='default'),
    Queue('lead_tasks', Exchange('lead_tasks'), routing_key='lead.#'),
    Queue('call_tasks', Exchange('call_tasks'), routing_key='call.#'),
    Queue('analytics_tasks', Exchange('analytics_tasks'), routing_key='analytics.#'),
    Queue('campaign_tasks', Exchange('campaign_tasks'), routing_key='campaign.#'),
)

# Task routes
task_routes = {
    # Lead tasks
    'backend.tasks.lead.*': {'queue': 'lead_tasks', 'routing_key': 'lead.tasks'},
    
    # Call tasks
    'backend.tasks.call.*': {'queue': 'call_tasks', 'routing_key': 'call.tasks'},
    
    # Analytics tasks
    'backend.tasks.analytics.*': {'queue': 'analytics_tasks', 'routing_key': 'analytics.tasks'},
    
    # Campaign tasks
    'backend.tasks.campaign.*': {'queue': 'campaign_tasks', 'routing_key': 'campaign.tasks'},
}

# Configure retry settings
task_publish_retry = True
task_publish_retry_policy = {
    'max_retries': 3,
    'interval_start': 0,
    'interval_step': 0.2,
    'interval_max': 0.5,
}

# Beat schedule for periodic tasks (if needed)
# beat_schedule = {
#     'daily-report-generation': {
#         'task': 'backend.tasks.analytics.generate_metrics.generate_daily_metrics',
#         'schedule': 86400.0,  # 24 hours
#     },
# } 
