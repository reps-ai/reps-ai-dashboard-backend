"""
Celery application factory and configuration.
"""
from celery import Celery
from backend.config.celery_settings import CelerySettings


def create_celery_app(settings: CelerySettings = None) -> Celery:
    """
    Create and configure a Celery application instance.
    
    Args:
        settings: Optional CelerySettings instance. If not provided, default settings are used.
        
    Returns:
        Configured Celery application instance.
    """
    if settings is None:
        settings = CelerySettings()
    
    app = Celery("reps_ai")
    
    # Configure Celery from settings
    app.conf.update(
        broker_url=settings.BROKER_URL,
        result_backend=settings.RESULT_BACKEND,
        task_serializer=settings.TASK_SERIALIZER,
        result_serializer=settings.RESULT_SERIALIZER,
        accept_content=settings.ACCEPT_CONTENT,
        timezone=settings.TIMEZONE,
        enable_utc=settings.ENABLE_UTC,
        task_track_started=settings.TASK_TRACK_STARTED,
        task_time_limit=settings.TASK_TIME_LIMIT,
        worker_concurrency=settings.WORKER_CONCURRENCY,
        beat_schedule=settings.BEAT_SCHEDULE,
        task_routes=settings.TASK_ROUTES,
    )
    
    # Auto-discover tasks in the specified packages
    app.autodiscover_tasks(["backend.tasks.lead", 
                           "backend.tasks.reports", 
                           "backend.tasks.notifications",
                           "backend.tasks.call"])
    
    return app


# Create a global Celery app instance for easy importing
app = create_celery_app()

if __name__ == '__main__':
    app.start() 