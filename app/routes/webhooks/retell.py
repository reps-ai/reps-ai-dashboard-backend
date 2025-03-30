"""
Webhook endpoint for Retell webhook events.
"""
from fastapi import APIRouter, Request, BackgroundTasks, HTTPException, Depends, Header
from typing import Dict, Any, Optional
import uuid
import json

from backend.services.call.factory import create_call_service
from backend.utils.logging.logger import get_logger
from backend.db.connections.database import get_db
from backend.tasks.call.task_definitions import process_retell_call

logger = get_logger(__name__)

router = APIRouter(prefix="/webhooks/retell", tags=["webhooks"])

# Helper to process webhook event and trigger Celery task
async def process_webhook_event(event_data: Dict[str, Any]):
    """Process a webhook event asynchronously and trigger Celery task."""
    logger.info(f"Processing webhook event in background: {event_data.get('event')}")
    
    # Get a database session and create the service
    async with get_db() as db:
        call_service = create_call_service(config={"enable_retell": True})
        
        try:
            # Add source to identify it as a Retell webhook
            event_data["source"] = "retell"
            
            # First, let the service process the webhook to extract necessary data
            result = await call_service.process_webhook_event(event_data)
            logger.info(f"Webhook processing result: {result.get('status')}")
            
            if result.get("status") == "error":
                logger.error(f"Error processing webhook: {result.get('message')}")
                return result
                
            # Extract data for Celery task
            call_data = result.get("call")
            if not call_data:
                logger.warning("No call data found in webhook processing result")
                return result
                
            call_id = call_data.get("id")
            
            # If we have a call ID and an event to process, queue Celery task
            if call_id:
                # Get event data to pass to Celery
                event_type = result.get("event_type")
                
                # Prepare data for Celery task
                celery_data = {
                    "event": event_data.get("event"),
                    "event_type": event_type
                }
                
                # Extract the call_id from the processed webhook (might be in various formats)
                retell_call_id = None
                
                # First try to get external_call_id from the call record
                if call_data.get("external_call_id"):
                    retell_call_id = str(call_data.get("external_call_id"))
                    celery_data["call_id"] = retell_call_id
                    logger.info(f"Using external_call_id from database: {retell_call_id}")
                # Then try to get it from the result
                elif result.get("call_id"):
                    retell_call_id = result.get("call_id")
                    celery_data["call_id"] = retell_call_id
                    logger.info(f"Using call_id from webhook result: {retell_call_id}")
                # Finally, look in the raw event data
                elif event_data.get("call", {}).get("call_id"):
                    retell_call_id = event_data.get("call", {}).get("call_id")
                    celery_data["call_id"] = retell_call_id
                    logger.info(f"Using call_id from raw webhook data: {retell_call_id}")
                
                # Add more data based on event type
                if event_type == "call.ended":
                    celery_data.update({
                        "recording_url": result.get("recording_url"),
                        "transcript": result.get("transcript"),
                        "end_timestamp": result.get("timestamp"),
                        "start_timestamp": call_data.get("start_time")
                    })
                elif event_type == "call.analyzed":
                    celery_data.update({
                        "call_analysis": {
                            "call_summary": result.get("summary"),
                            "user_sentiment": result.get("sentiment")
                        }
                    })
                
                # Queue the Celery task
                logger.info(f"Queuing Celery task to process webhook data for call {call_id}")
                process_retell_call.delay(call_id, celery_data)
                
                # Also, if this is the first event (e.g., call.started), update the external_call_id if needed
                if event_type == "call.started" and retell_call_id and not call_data.get("external_call_id"):
                    # Clean call ID if needed (remove prefixes)
                    clean_call_id = retell_call_id
                    if isinstance(clean_call_id, str) and clean_call_id.startswith("call_"):
                        clean_call_id = clean_call_id[5:]
                        
                    # Update the call record with the external_call_id directly
                    logger.info(f"Updating call {call_id} with external_call_id: {clean_call_id}")
                    await call_service.call_repository.update_call(call_id, {
                        "external_call_id": clean_call_id
                    })
                
                return {
                    "status": "success", 
                    "message": "Webhook processed and Celery task queued",
                    "call_id": call_id
                }
            else:
                logger.warning("No call ID found in processed webhook data")
                return {"status": "error", "message": "No call ID found"}
            
        except Exception as e:
            logger.error(f"Error processing webhook event: {str(e)}")
            return {"status": "error", "message": str(e)}

@router.post("")
async def receive_retell_webhook(
    request: Request, 
    background_tasks: BackgroundTasks,
    x_retell_signature: Optional[str] = Header(None)
):
    """
    Receive and process Retell webhook events.
    
    This endpoint receives webhooks from Retell, validates them, and processes them
    in the background. It uses FastAPI's BackgroundTasks to process the webhook
    asynchronously and return an immediate response to Retell.
    """
    try:
        # Parse webhook body
        event_data = await request.json()
        logger.info(f"Received Retell webhook: {event_data.get('event')}")
        
        # Extract call data
        call_data = event_data.get("call", {})
        logger.info(f"Webhook call data: {call_data}")
        
        # TODO: Verify the webhook signature (x_retell_signature) in production
        
        # Process the webhook in the background
        background_tasks.add_task(process_webhook_event, event_data)
        
        # Return 200 OK immediately to acknowledge receipt
        return {"status": "success", "message": "Webhook received and processing started"}
    except Exception as e:
        logger.error(f"Error handling Retell webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing webhook: {str(e)}") 