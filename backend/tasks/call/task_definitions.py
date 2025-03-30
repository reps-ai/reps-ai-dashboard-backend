"""
Task definitions for call-related background jobs.
"""
from typing import Dict, Any
from datetime import datetime
import asyncio
import uuid

from ...celery_app import app
from ...db.repositories.call.implementations.postgres_call_repository import PostgresCallRepository
from ...db.connections.database import SessionLocal
from ...utils.logging.logger import get_logger
from ...integrations.retell.factory import create_retell_integration

logger = get_logger(__name__)

def run_async(coro):
    """Run an async coroutine in a synchronous context, properly isolating the event loop."""
    try:
        # Create a new event loop for this task
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)
    finally:
        # Properly close the loop to avoid resource leaks
        if loop and not loop.is_closed():
            # Cancel any remaining tasks
            for task in asyncio.all_tasks(loop):
                task.cancel()
            loop.close()

@app.task(
    name='call.create_retell_call',
    queue='call_tasks',
    bind=True,
    retry_backoff=True,
    max_retries=3
)
def create_retell_call(self, db_call_id: str, lead_data: Dict[str, Any], campaign_id: str = None) -> bool:
    """
    Create a Retell call as a background task and update the database with the result.
    
    Args:
        db_call_id: ID of the call in our database
        lead_data: Dictionary containing lead information
        campaign_id: Optional ID of the campaign
        
    Returns:
        Boolean indicating if the operation was successful
    """
    try:
        logger.info(f"Creating Retell call for database call ID: {db_call_id}")
        
        # Define async function to handle the call creation and database updates
        async def create_call_and_update_db():
            # Get database session
            db = SessionLocal()
            try:
                # Create repository
                repository = PostgresCallRepository(db)
                
                # Create Retell integration
                retell_integration = create_retell_integration()
                
                # Make the call using Retell
                retell_call_result = await retell_integration.create_call(
                    lead_data=lead_data,
                    campaign_id=campaign_id
                )
                
                # Prepare update data
                update_data = {}
                
                if retell_call_result.get("status") == "error":
                    # Handle error from Retell
                    logger.error(f"Error from Retell: {retell_call_result.get('message')}")
                    update_data = {
                        "call_status": "error",
                        "human_notes": f"Retell error: {retell_call_result.get('message')}"
                    }
                else:
                    # Extract call status and ID from Retell
                    call_status = retell_call_result.get("call_status", "scheduled")
                    retell_call_id = retell_call_result.get("call_id")
                    
                    # Update with Retell data
                    update_data = {
                        "call_status": call_status,
                        "external_call_id": retell_call_id
                    }
                    
                    # If we got a successful call, schedule polling for updates
                    if retell_call_id:
                        # Schedule first polling attempt after 2 minutes
                        app.send_task(
                            'call.poll_retell_call_status',
                            args=[db_call_id, retell_call_id, 1],
                            countdown=120  # 2 minutes
                        )
                        logger.info(f"Scheduled first polling task for call {db_call_id} in 2 minutes")
                
                # Update the call record
                updated_call = await repository.update_call(db_call_id, update_data)
                
                if not updated_call:
                    logger.error(f"Failed to update call {db_call_id}")
                    return False
                
                # Commit the transaction
                await db.commit()
                
                logger.info(f"Successfully created Retell call for {db_call_id}")
                return True
            except Exception as e:
                logger.error(f"Database error in create_call_and_update_db: {str(e)}")
                # Rollback on error
                await db.rollback()
                # Re-raise to trigger retry
                raise
            finally:
                # Close the session
                await db.close()
        
        # Run the async function
        result = run_async(create_call_and_update_db())
        return result
        
    except Exception as e:
        logger.error(f"Error creating Retell call for call {db_call_id}: {str(e)}")
        # Retry the task with exponential backoff
        self.retry(exc=e, countdown=60)
        return False

@app.task(
    name='call.process_retell_call',
    queue='call_tasks',
    bind=True,
    retry_backoff=True,
    max_retries=3
)
def process_retell_call(self, db_call_id: str, retell_call_data: Dict[str, Any]) -> bool:
    """
    Process a completed Retell call and update our database.
    
    This task should be triggered when a call completes in Retell, either through
    a webhook callback or when a call is completed.
    
    Args:
        db_call_id: ID of the call in our database
        retell_call_data: Complete call data from Retell
    """
    try:
        logger.info(f"Processing Retell call data for call ID: {db_call_id}")
        
        # Initialize the update data dictionary with sensible defaults
        update_data = {
            "call_status": "in_progress"  # Default status if we can't determine completion
        }
        
        # Extract the Retell call ID and store it as is
        retell_call_id = retell_call_data.get("call_id")
        if retell_call_id:
            # If it's a string like "call_abc123", extract just the ID part
            if isinstance(retell_call_id, str) and retell_call_id.startswith("call_"):
                retell_call_id = retell_call_id[5:]  # Remove the "call_" prefix
            
            # Store directly as string
            update_data["external_call_id"] = retell_call_id
            logger.info(f"Storing external call ID: {retell_call_id}")
        
        # Extract timestamp data if available
        if retell_call_data.get("start_timestamp"):
            update_data["start_time"] = datetime.fromtimestamp(retell_call_data["start_timestamp"] / 1000)
        
        if retell_call_data.get("end_timestamp"):
            update_data["end_time"] = datetime.fromtimestamp(retell_call_data["end_timestamp"] / 1000)
            # If we have both timestamps, we can calculate duration
            if retell_call_data.get("start_timestamp"):
                update_data["duration"] = (retell_call_data["end_timestamp"] - retell_call_data["start_timestamp"]) // 1000
                # If we have an end timestamp, the call is likely completed
                update_data["call_status"] = "completed"
        
        # Add media data if available
        if retell_call_data.get("recording_url"):
            update_data["recording_url"] = retell_call_data["recording_url"]
        
        if retell_call_data.get("transcript"):
            update_data["transcript"] = retell_call_data["transcript"]
        
        # Add analysis data if available
        if retell_call_data.get("call_analysis"):
            analysis = retell_call_data["call_analysis"]
            if analysis.get("call_summary"):
                update_data["summary"] = analysis["call_summary"]
            
            if analysis.get("user_sentiment"):
                update_data["sentiment"] = analysis["user_sentiment"].lower()
        
        # Define the async function to handle database operations
        async def update_call_db():
            # Get database session
            db = SessionLocal()
            try:
                repository = PostgresCallRepository(db)
                
                # Get current call state
                current_call = await repository.get_call_by_id(db_call_id)
                
                # If call not found, log and return
                if not current_call:
                    logger.error(f"Call with ID {db_call_id} not found")
                    return False
                
                # Don't overwrite completed/error state with in_progress
                if current_call.get("call_status") in ["completed", "error"]:
                    if update_data.get("call_status") == "in_progress":
                        update_data.pop("call_status", None)
                
                # Update the call record
                updated_call = await repository.update_call(db_call_id, update_data)
                
                if not updated_call:
                    logger.error(f"Failed to update call {db_call_id}")
                    return False
                    
                # Explicitly commit changes
                await db.commit()
                
                logger.info(f"Successfully updated call {db_call_id}")
                return True
            except Exception as e:
                logger.error(f"Database error: {str(e)}")
                # Explicitly rollback on error
                await db.rollback()
                # Re-raise to trigger retry
                raise
            finally:
                # Make sure to properly close the session
                await db.close()
        
        # Run the async function with proper error handling
        result = run_async(update_call_db())
        return result
        
    except Exception as e:
        logger.error(f"Error processing Retell call data for call {db_call_id}: {str(e)}")
        # Retry the task with exponential backoff
        self.retry(exc=e, countdown=60)
        return False

@app.task(
    name='call.poll_retell_call_status',
    queue='call_tasks',
    bind=True,
    retry_backoff=True,
    max_retries=3
)
def poll_retell_call_status(self, db_call_id: str, external_call_id: str, attempt: int = 1) -> bool:
    """
    Poll Retell API for call status updates as a backup for webhooks.
    
    This task is scheduled after a call is created as a fallback in case
    webhook notifications are missed. It checks at increasing intervals:
    1. First check: 2 minutes after call creation
    2. Second check: 5 minutes after first check
    3. Third check: 15 minutes after second check
    4. Final check: 30 minutes after call creation (mark as error if still pending)
    
    Args:
        db_call_id: ID of the call in our database
        external_call_id: ID of the call in Retell (now a string)
        attempt: Current polling attempt (1-4)
    """
    logger.info(f"Polling Retell for call status: call ID {db_call_id}, attempt {attempt}")
    
    try:
        # Define the async function to handle API call and database operations
        async def check_call_status():
            # Get database session
            db = SessionLocal()
            try:
                # Create repository
                repository = PostgresCallRepository(db)
                
                # First, check if call is already completed (to avoid unnecessary API calls)
                current_call = await repository.get_call_by_id(db_call_id)
                
                if not current_call:
                    logger.error(f"Call with ID {db_call_id} not found")
                    return False
                
                # If call is already completed or in error state, no need to poll
                if current_call.get("call_status") in ["completed", "error"]:
                    logger.info(f"Call {db_call_id} already in final state: {current_call.get('call_status')}, no polling needed")
                    return True
                
                # Create Retell integration
                retell_integration = create_retell_integration()
                
                # Get call status from Retell
                call_status_result = await retell_integration.get_call_status(external_call_id)
                
                # Check if API call was successful
                if call_status_result.get("status") == "error":
                    logger.error(f"Error getting call status from Retell: {call_status_result.get('message')}")
                    
                    # If final attempt and call still not updated, mark as error
                    if attempt >= 4:
                        error_update = {
                            "call_status": "error",
                            "human_notes": f"{current_call.get('human_notes', '')} | Error in final polling attempt: {call_status_result.get('message')}"
                        }
                        await repository.update_call(db_call_id, error_update)
                        await db.commit()
                        logger.warning(f"Marked call {db_call_id} as error after final polling attempt")
                    
                    return False
                
                # If successful, process call data
                call_data = {
                    "call_id": external_call_id,
                    "call_status": call_status_result.get("call_status"),
                    "start_timestamp": call_status_result.get("start_timestamp"),
                    "end_timestamp": call_status_result.get("end_timestamp"),
                    "recording_url": call_status_result.get("recording_url"),
                    "transcript": call_status_result.get("transcript"),
                    "call_analysis": call_status_result.get("call_analysis", {})
                }
                
                # Process the data using the existing task
                from backend.celery_app import app as celery_app
                celery_app.send_task(
                    'call.process_retell_call',
                    args=[db_call_id, call_data]
                )
                
                logger.info(f"Successfully polled Retell for call {db_call_id}, status: {call_data.get('call_status')}")
                
                # Schedule next polling attempt if needed
                if call_data.get("call_status") not in ["completed", "failed", "error"]:
                    if attempt == 1:
                        # Second check after 5 minutes
                        celery_app.send_task(
                            'call.poll_retell_call_status',
                            args=[db_call_id, external_call_id, 2],
                            countdown=300  # 5 minutes
                        )
                        logger.info(f"Scheduled second polling attempt for call {db_call_id} in 5 minutes")
                    elif attempt == 2:
                        # Third check after 15 minutes
                        celery_app.send_task(
                            'call.poll_retell_call_status',
                            args=[db_call_id, external_call_id, 3],
                            countdown=900  # 15 minutes
                        )
                        logger.info(f"Scheduled third polling attempt for call {db_call_id} in 15 minutes")
                    elif attempt == 3:
                        # Final check (only if 30 minutes haven't passed yet)
                        celery_app.send_task(
                            'call.poll_retell_call_status',
                            args=[db_call_id, external_call_id, 4],
                            countdown=600  # 10 minutes (30 min total from start)
                        )
                        logger.info(f"Scheduled final polling attempt for call {db_call_id} in 10 minutes")
                    elif attempt >= 4:
                        # If still not completed after final check, mark as error
                        error_update = {
                            "call_status": "error",
                            "human_notes": f"{current_call.get('human_notes', '')} | Call timed out after 30 minutes"
                        }
                        await repository.update_call(db_call_id, error_update)
                        await db.commit()
                        logger.warning(f"Marked call {db_call_id} as error after timeout")
                
                return True
            except Exception as e:
                logger.error(f"Error in check_call_status: {str(e)}")
                await db.rollback()
                raise
            finally:
                await db.close()
        
        # Run the async function
        result = run_async(check_call_status())
        return result
        
    except Exception as e:
        logger.error(f"Error polling Retell call status for call {db_call_id}: {str(e)}")
        # Retry the task with exponential backoff
        self.retry(exc=e, countdown=30)
        return False
