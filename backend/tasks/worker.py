"""
Celery worker configuration.

This module provides configuration and utilities for Celery workers.
It can be used as an entry point to start workers with custom configuration.
"""
import os
import sys
import logging
import subprocess
from backend.celery_app import app

logger = logging.getLogger(__name__)

def check_redis():
    """
    Check if Redis is running and accessible.
    
    Returns:
        bool: True if Redis is running, False otherwise
    """
    try:
        # Simple check to see if we can connect to Redis
        broker_url = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")  # <-- FIXED DEFAULT
        
        # If we're using a different broker, skip Redis check
        if not broker_url.startswith("redis://"):
            return True
            
        # Try to ping Redis
        import redis
        host = broker_url.split("//")[1].split(":")[0]
        port = int(broker_url.split(":")[2].split("/")[0])
        db = int(broker_url.split("/")[-1])
        
        r = redis.Redis(host=host, port=port, db=db)
        r.ping()
        return True
    except Exception as e:
        logger.error(f"Redis check failed: {str(e)}")
        return False

def start_worker(queue='default', concurrency=None, loglevel='INFO'):
    """
    Start a Celery worker with the specified queue and concurrency.
    
    Args:
        queue: Queue name or comma-separated list of queue names
        concurrency: Number of worker processes/threads
        loglevel: Logging level
    """
    # Check if Redis is running
    if not check_redis():
        logger.error("Redis is not running. Please start Redis before starting workers.")
        print("Error: Redis is not running. Please start Redis before starting workers.")
        sys.exit(1)
    
    # Prepare Celery worker arguments
    args = ['worker', '-Q', queue, '--loglevel', loglevel]
    
    if concurrency:
        args.extend(['--concurrency', str(concurrency)])
    
    logger.info(f"Starting Celery worker for queue(s): {queue}")
    app.worker_main(args)

if __name__ == '__main__':
    # Configure basic logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Example usage: python -m backend.tasks.worker lead_tasks 4
    
    # Default to 'default' queue if not specified
    queue = sys.argv[1] if len(sys.argv) > 1 else 'default'
    
    # Get concurrency from environment or command line
    concurrency = None
    if len(sys.argv) > 2:
        concurrency = int(sys.argv[2])
    elif os.getenv('WORKER_CONCURRENCY'):
        concurrency = int(os.getenv('WORKER_CONCURRENCY'))
    
    # Get log level from environment or command line
    loglevel = 'INFO'
    if len(sys.argv) > 3:
        loglevel = sys.argv[3]
    elif os.getenv('WORKER_LOGLEVEL'):
        loglevel = os.getenv('WORKER_LOGLEVEL')
    
    # Start the worker
    start_worker(queue=queue, concurrency=concurrency, loglevel=loglevel)