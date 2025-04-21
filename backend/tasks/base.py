"""
Base task class for all Celery tasks.
"""
import logging
from typing import Any, Dict, Optional, Tuple, Type
from celery import Task

from backend.celery_app import app


class BaseTask(Task):
    """
    Base task class with common functionality for all tasks.
    
    Features:
    - Automatic retry on exceptions
    - Standardized logging
    - Service dependency injection capability
    """
    
    # Default retry settings
    autoretry_for = (Exception,)
    retry_kwargs = {'max_retries': 3}
    retry_backoff = True
    retry_backoff_max = 600  # 10 minutes
    retry_jitter = True
    
    # Name to use when registering with Celery
    name: Optional[str] = None
    
    # Service class to be injected (should be overridden in subclasses)
    service_class: Optional[Type] = None
    
    def __init__(self) -> None:
        """Initialize the task with a logger."""
        self.logger = logging.getLogger(self.name or self.__class__.__name__)
    
    def get_service(self) -> Any:
        """
        Create an instance of the service class.
        
        Returns:
            Instance of the service class configured for this task.
        
        Raises:
            ValueError: If service_class is not defined.
        """
        if not self.service_class:
            raise ValueError(f"Task {self.name} has no service_class defined")
        
        return self.service_class()
    
    def run(self, *args: Any, **kwargs: Any) -> Any:
        """
        Execute the task. Should be implemented by subclasses.
        
        Args:
            *args: Positional arguments for the task.
            **kwargs: Keyword arguments for the task.
            
        Returns:
            The result of the task.
            
        Raises:
            NotImplementedError: If the subclass does not implement this method.
        """
        raise NotImplementedError("Subclasses must implement the run method")
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """
        Handle task failure.
        
        Args:
            exc: The exception raised by the task.
            task_id: The ID of the task.
            args: The positional arguments passed to the task.
            kwargs: The keyword arguments passed to the task.
            einfo: Exception info object.
        """
        self.logger.error(
            f"Task {self.name} failed: {exc}",
            exc_info=True,
            extra={
                "task_id": task_id,
                "args": args,
                "kwargs": kwargs,
            }
        )
        super().on_failure(exc, task_id, args, kwargs, einfo)
    
    def on_success(self, retval, task_id, args, kwargs):
        """
        Handle task success.
        
        Args:
            retval: The return value of the task.
            task_id: The ID of the task.
            args: The positional arguments passed to the task.
            kwargs: The keyword arguments passed to the task.
        """
        self.logger.info(
            f"Task {self.name} succeeded",
            extra={
                "task_id": task_id,
                "result": retval,
            }
        )
        super().on_success(retval, task_id, args, kwargs)


# Define a function-based task decorator
def task(*args, **kwargs):
    """
    Decorator that registers a function as a Celery task.
    
    Args:
        *args: Positional arguments to pass to Celery's task decorator.
        **kwargs: Keyword arguments to pass to Celery's task decorator.
        
    Returns:
        A decorated function registered as a Celery task.
    """
    kwargs.setdefault('base', BaseTask)
    return app.task(*args, **kwargs) 