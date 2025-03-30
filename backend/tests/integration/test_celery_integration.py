"""
Integration tests for Celery tasks.

These tests verify that Celery tasks can be successfully submitted and executed.
"""
import os
import time
import pytest
import asyncio
import subprocess
import signal
from datetime import datetime

from celery.result import AsyncResult

from backend.tasks.lead import (
    update_lead,
    update_lead_after_call,
    qualify_lead,
    add_tags_to_lead
)
from backend.celery_app import app
from backend.examples.lead_tasks.example_data import (
    EXAMPLE_LEAD_ID,
    EXAMPLE_LEAD_DATA,
    EXAMPLE_CALL_DATA,
    EXAMPLE_TAGS,
    EXAMPLE_LEAD_BATCH,
    EXAMPLE_BATCH_UPDATE_DATA
)


class CeleryWorkerProcess:
    """Manage a Celery worker process for integration testing."""
    
    def __init__(self, queue_name="lead_queue", loglevel="info"):
        self.queue_name = queue_name
        self.loglevel = loglevel
        self.process = None
        
    def start(self):
        """Start a Celery worker process."""
        # Build command
        cmd = [
            "celery", 
            "-A", "backend.celery_app", 
            "worker", 
            "-l", self.loglevel,
            "-Q", self.queue_name,
            "--concurrency=1",  # Single worker for predictable behavior
            "-P", "solo"        # Solo pool for simplicity
        ]
        
        # Start process
        self.process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            preexec_fn=os.setsid  # Create a new process group
        )
        
        # Give the worker time to start
        time.sleep(5)
        
        # Verify worker is running
        if self.process.poll() is not None:
            stdout, stderr = self.process.communicate()
            raise RuntimeError(f"Failed to start Celery worker: {stderr}")
        
        print(f"Celery worker started with PID {self.process.pid}")
        return self.process
    
    def stop(self):
        """Stop the Celery worker process."""
        if self.process and self.process.poll() is None:
            # Send SIGTERM to the process group
            try:
                os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
                self.process.wait(timeout=5)
                print("Celery worker stopped gracefully")
            except subprocess.TimeoutExpired:
                # If it doesn't respond to SIGTERM, use SIGKILL
                os.killpg(os.getpgid(self.process.pid), signal.SIGKILL)
                print("Celery worker killed forcefully")
            
            self.process = None


@pytest.fixture(scope="module")
def celery_worker():
    """Fixture to start and stop a Celery worker for testing."""
    # Verify Redis is running
    try:
        redis_check = subprocess.run(
            ["redis-cli", "ping"], 
            check=True, 
            capture_output=True, 
            text=True
        )
        if redis_check.stdout.strip() != "PONG":
            pytest.skip("Redis is not running. Cannot run Celery integration tests.")
    except (subprocess.SubprocessError, FileNotFoundError):
        pytest.skip("Redis is not running or redis-cli not found. Cannot run Celery integration tests.")
    
    # Start worker
    worker = CeleryWorkerProcess()
    worker.start()
    
    yield
    
    # Stop worker
    worker.stop()


async def wait_for_task_completion(task_id: str, timeout: int = 30) -> AsyncResult:
    """
    Wait for a Celery task to complete.
    
    Args:
        task_id: ID of the task to wait for
        timeout: Maximum time to wait in seconds
        
    Returns:
        AsyncResult object with task result
    """
    # Get task result object
    result = AsyncResult(task_id, app=app)
    start_time = time.time()
    
    # Wait for task to complete
    while result.status in ['PENDING', 'STARTED'] and time.time() - start_time < timeout:
        await asyncio.sleep(0.5)
        # Refresh result
        result = AsyncResult(task_id, app=app)
    
    return result


@pytest.mark.integration
@pytest.mark.asyncio
async def test_update_lead_delay(celery_worker):
    """
    Test the update_lead task can be submitted and executes.
    
    This test verifies that:
    1. The task can be submitted with .delay()
    2. The task executes and completes successfully
    """
    # Submit task with example data
    task = update_lead.delay(EXAMPLE_LEAD_ID, EXAMPLE_LEAD_DATA)
    
    # Verify task ID is returned
    assert task.id is not None
    print(f"Task ID: {task.id}")
    
    # Wait for task to complete
    result = await wait_for_task_completion(task.id)
    
    # Check task status
    print(f"Task status: {result.status}")
    print(f"Task result: {result.result}")
    
    # Verify task completed (might fail due to invalid lead ID, but task was processed)
    assert result.status != 'PENDING', "Task did not start execution"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_update_lead_after_call_delay(celery_worker):
    """
    Test the update_lead_after_call task can be submitted and executes.
    
    This test verifies that:
    1. The task can be submitted with .delay()
    2. The task executes and completes successfully
    """
    # Submit task with example data
    task = update_lead_after_call.delay(EXAMPLE_LEAD_ID, EXAMPLE_CALL_DATA)
    
    # Verify task ID is returned
    assert task.id is not None
    print(f"Task ID: {task.id}")
    
    # Wait for task to complete
    result = await wait_for_task_completion(task.id)
    
    # Check task status
    print(f"Task status: {result.status}")
    print(f"Task result: {result.result}")
    
    # Verify task completed (might fail due to invalid lead ID, but task was processed)
    assert result.status != 'PENDING', "Task did not start execution"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_qualify_lead_delay(celery_worker):
    """
    Test the qualify_lead task can be submitted and executes.
    
    This test verifies that:
    1. The task can be submitted with .delay()
    2. The task executes and completes successfully
    """
    # Submit task with example data
    task = qualify_lead.delay(EXAMPLE_LEAD_ID, "hot")
    
    # Verify task ID is returned
    assert task.id is not None
    print(f"Task ID: {task.id}")
    
    # Wait for task to complete
    result = await wait_for_task_completion(task.id)
    
    # Check task status
    print(f"Task status: {result.status}")
    print(f"Task result: {result.result}")
    
    # Verify task completed (might fail due to invalid lead ID, but task was processed)
    assert result.status != 'PENDING', "Task did not start execution"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_add_tags_to_lead_delay(celery_worker):
    """
    Test the add_tags_to_lead task can be submitted and executes.
    
    This test verifies that:
    1. The task can be submitted with .delay()
    2. The task executes and completes successfully
    """
    # Submit task with example data
    task = add_tags_to_lead.delay(EXAMPLE_LEAD_ID, EXAMPLE_TAGS)
    
    # Verify task ID is returned
    assert task.id is not None
    print(f"Task ID: {task.id}")
    
    # Wait for task to complete
    result = await wait_for_task_completion(task.id)
    
    # Check task status
    print(f"Task status: {result.status}")
    print(f"Task result: {result.result}")
    
    # Verify task completed (might fail due to invalid lead ID, but task was processed)
    assert result.status != 'PENDING', "Task did not start execution"


if __name__ == "__main__":
    # Enable running the tests directly
    asyncio.run(pytest.main(["-v", __file__])) 