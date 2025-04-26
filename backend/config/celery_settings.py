"""
Celery configuration settings using Pydantic.
"""
from typing import Dict, List, Any
from pydantic_settings import BaseSettings
from celery.schedules import crontab


class CelerySettings(BaseSettings):
    """Settings for Celery configuration."""
    
    # Core Celery settings
    BROKER_URL: str = "redis://redis:6379/0"
    RESULT_BACKEND: str = "redis://redis:6379/0"
    TASK_SERIALIZER: str = "json"
    RESULT_SERIALIZER: str = "json"
    ACCEPT_CONTENT: List[str] = ["json"]
    TIMEZONE: str = "UTC"
    ENABLE_UTC: bool = True
    
    # Task settings
    TASK_TRACK_STARTED: bool = True
    TASK_TIME_LIMIT: int = 60 * 5  # 5 minutes
    WORKER_CONCURRENCY: int = 4
    
    # Task routing
    TASK_ROUTES: Dict[str, Dict[str, str]] = {
        "backend.tasks.call.process_completed_call": {"queue": "call_tasks"},
        "backend.tasks.call.*": {"queue": "call_tasks"},  # Route all call tasks to call_tasks queue
        "backend.tasks.lead.*": {"queue": "lead_tasks"},  # Route all lead tasks to lead_tasks queue
        "backend.tasks.reports.*": {"queue": "reports_tasks"},  # Route all report tasks to reports_tasks queue
        "backend.tasks.notifications.*": {"queue": "notification_tasks"},  # Route all notification tasks to notification_tasks queue
    }
    
    # Beat schedule for periodic tasks
    BEAT_SCHEDULE: Dict[str, Any] = {
        # Qualify leads after calls (runs every 15 minutes)
        "qualify-leads": {
            "task": "backend.tasks.lead.tasks.qualify_pending_leads",
            "schedule": crontab(minute="*/15"),
        },
        
        # Check for scheduled reports (runs every minute)
        "check-scheduled-reports": {
            "task": "backend.tasks.reports.check_scheduled_reports",
            "schedule": crontab(minute="*"),
        },
        
        # Process pending reports (runs every 5 minutes)
        "process-pending-reports": {
            "task": "backend.tasks.reports.process_pending_reports",
            "schedule": crontab(minute="*/5"),
        },
        
        # Generate daily lead reports (runs at 1:00 AM)
        "generate-daily-lead-reports": {
            "task": "backend.tasks.reports.generate_daily_lead_report",
            "schedule": crontab(hour=1, minute=0),
        },
        
        # Generate weekly lead reports (runs at 2:00 AM on Mondays)
        "generate-weekly-lead-reports": {
            "task": "backend.tasks.reports.generate_weekly_lead_report",
            "schedule": crontab(hour=2, minute=0, day_of_week="monday"),
        },
        
        # Generate daily reports (runs at midnight)
        "generate-daily-reports": {
            "task": "backend.tasks.reports.tasks.generate_daily_call_report",
            "schedule": crontab(hour=0, minute=0),
        },
        
        # Send emails to gym faculty (runs at 9 AM every weekday)
        "send-faculty-notifications": {
            "task": "backend.tasks.notifications.tasks.send_faculty_notifications",
            "schedule": crontab(hour=9, minute=0, day_of_week="1-5"),
        },
        
        # Generate daily call reports for all branches (runs at 1 AM)
        "generate-branch-call-reports": {
            "task": "backend.tasks.call.report_tasks.generate_daily_branch_reports",
            "schedule": crontab(hour=1, minute=0),
        },
    }
    
    class Config:
        env_prefix = "CELERY_"
        case_sensitive = True 