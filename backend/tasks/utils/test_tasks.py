"""
Test tasks for verifying Celery and Redis setup.

These tasks are meant for testing the background task infrastructure
and should not be used in production.
"""
import time
from datetime import datetime

from backend.celery_app import app
from backend.utils.logging.logger import get_logger

logger = get_logger(__name__)

@app.task(name='test.add_numbers')
def add_numbers(x, y):
    """
    Simple test task that adds two numbers with a deliberate delay
    to simulate a time-consuming operation.
    
    Args:
        x: First number
        y: Second number
        
    Returns:
        The sum and timestamp
    """
    logger.info(f"Task started: Adding {x} + {y}")
    
    # Simulate time-consuming work
    time.sleep(5)
    
    result = x + y
    timestamp = datetime.now().isoformat()
    
    logger.info(f"Task completed: {x} + {y} = {result}")
    
    return {
        "result": result,
        "timestamp": timestamp,
        "task_id": add_numbers.request.id,
    }

@app.task(name='test.log_message')
def log_message(message):
    """
    Simple task to log a message.
    
    Args:
        message: Message to log
        
    Returns:
        Confirmation with timestamp
    """
    timestamp = datetime.now().isoformat()
    logger.info(f"Message at {timestamp}: {message}")
    
    # Simulate some work
    time.sleep(2)
    
    return {
        "message": message,
        "timestamp": timestamp,
        "task_id": log_message.request.id,
    } 