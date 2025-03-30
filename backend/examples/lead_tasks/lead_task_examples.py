"""
Example script for using lead background tasks.

This script demonstrates how to use the Celery tasks for lead processing.
"""
import asyncio
import time
from typing import Dict, Any

# Import task functions
from backend.tasks.lead import (
    update_lead,
    update_lead_after_call,
    qualify_lead,
    add_tags_to_lead,
    update_lead_batch
)

# Import example data
from backend.examples.lead_tasks.example_data import (
    EXAMPLE_LEAD_ID,
    EXAMPLE_LEAD_DATA,
    EXAMPLE_CALL_DATA,
    EXAMPLE_TAGS,
    EXAMPLE_LEAD_BATCH,
    EXAMPLE_BATCH_UPDATE_DATA
)

def demo_update_lead():
    """Demonstrate updating a lead as a background task."""
    print("\n== Demonstrating lead update background task ==")
    
    # Call the task
    print(f"Sending update for lead ID: {EXAMPLE_LEAD_ID}")
    result = update_lead.delay(EXAMPLE_LEAD_ID, EXAMPLE_LEAD_DATA)
    
    # Get task ID and status
    print(f"Task ID: {result.id}")
    print(f"Task status: {result.status}")
    print("Task sent to queue. Check Celery worker logs for execution details.")

def demo_update_lead_after_call():
    """Demonstrate updating a lead after a call as a background task."""
    print("\n== Demonstrating lead update after call background task ==")
    
    # Call the task
    print(f"Sending call update for lead ID: {EXAMPLE_LEAD_ID}")
    result = update_lead_after_call.delay(EXAMPLE_LEAD_ID, EXAMPLE_CALL_DATA)
    
    # Get task ID and status
    print(f"Task ID: {result.id}")
    print(f"Task status: {result.status}")
    print("Task sent to queue. Check Celery worker logs for execution details.")

def demo_qualify_lead():
    """Demonstrate qualifying a lead as a background task."""
    print("\n== Demonstrating lead qualification background task ==")
    
    # Call the task
    qualification = 1  # hot
    print(f"Sending qualification update (hot={qualification}) for lead ID: {EXAMPLE_LEAD_ID}")
    result = qualify_lead.delay(EXAMPLE_LEAD_ID, qualification)
    
    # Get task ID and status
    print(f"Task ID: {result.id}")
    print(f"Task status: {result.status}")
    print("Task sent to queue. Check Celery worker logs for execution details.")

def demo_add_tags_to_lead():
    """Demonstrate adding tags to a lead as a background task."""
    print("\n== Demonstrating add tags background task ==")
    
    # Call the task
    print(f"Adding tags {EXAMPLE_TAGS} to lead ID: {EXAMPLE_LEAD_ID}")
    result = add_tags_to_lead.delay(EXAMPLE_LEAD_ID, EXAMPLE_TAGS)
    
    # Get task ID and status
    print(f"Task ID: {result.id}")
    print(f"Task status: {result.status}")
    print("Task sent to queue. Check Celery worker logs for execution details.")

def demo_update_lead_batch():
    """Demonstrate batch updating leads as a background task."""
    print("\n== Demonstrating batch update background task ==")
    
    # Call the task
    print(f"Updating {len(EXAMPLE_LEAD_BATCH)} leads in batch")
    result = update_lead_batch.delay(EXAMPLE_LEAD_BATCH, EXAMPLE_BATCH_UPDATE_DATA)
    
    # Get task ID and status
    print(f"Task ID: {result.id}")
    print(f"Task status: {result.status}")
    print("Task sent to queue. Check Celery worker logs for execution details.")

def run_all_demos():
    """Run all demonstration functions."""
    demo_update_lead()
    time.sleep(1)  # Small delay between demos
    
    demo_update_lead_after_call()
    time.sleep(1)
    
    demo_qualify_lead()
    time.sleep(1)
    
    demo_add_tags_to_lead()
    time.sleep(1)
    
    demo_update_lead_batch()

if __name__ == "__main__":
    # Run all demos
    run_all_demos()
    
    print("\nAll tasks have been sent to the Celery worker.")
    print("Check the worker logs for execution details.")
    print("Remember to have Celery worker running with the lead_queue:")
    print("celery -A backend.celery_app worker -l info -Q lead_queue") 