"""
Celery tasks for call processing operations.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime

from backend.celery_app import app
from backend.services.call.factory import create_call_service
from backend.services.lead.factory import create_lead_service
from backend.services.campaign.factory import create_campaign_service
from backend.utils.logging.logger import get_logger

logger = get_logger(__name__)

@app.task(name='call.process_call_completion', bind=True, max_retries=3)
def process_call_completion(self, call_id: str, call_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process a call after it has been completed as a background task.
    
    Args:
        call_id: ID of the call
        call_data: Call data including outcome, notes, etc.
        
    Returns:
        Updated call data
    """
    logger.info(f"Background task: processing completion for call {call_id}")
    
    try:
        # Create service instances
        call_service = create_call_service()
        lead_service = create_lead_service()
        
        # Convert to awaitable result
        import asyncio
        
        # Update call with completion data
        call = asyncio.run(call_service.update_call(call_id, {
            "status": "completed",
            "end_time": datetime.now().isoformat(),
            "outcome": call_data.get("outcome"),
            "notes": call_data.get("notes")
        }))
        
        if not call:
            logger.error(f"Call {call_id} not found")
            raise ValueError(f"Call {call_id} not found")
        
        # Update lead based on call outcome
        lead_id = call.get("lead_id")
        if lead_id:
            logger.info(f"Updating lead {lead_id} based on call outcome")
            
            # Prepare lead update data
            lead_update_data = {
                "last_call_date": datetime.now().isoformat()
            }
            
            # Update lead status based on outcome
            outcome = call_data.get("outcome")
            if outcome == "scheduled":
                lead_update_data["status"] = "scheduled"
            elif outcome == "not_interested":
                lead_update_data["status"] = "closed"
            elif outcome == "callback":
                lead_update_data["status"] = "callback"
                
                # If callback requested, add callback date if provided
                if "callback_date" in call_data:
                    lead_update_data["callback_date"] = call_data["callback_date"]
            
            # Update lead
            asyncio.run(lead_service.update_lead(lead_id, lead_update_data))
            
            # Update lead qualification if needed
            if "qualification" in call_data:
                asyncio.run(lead_service.qualify_lead(lead_id, call_data["qualification"]))
            
            # Add tags if provided
            if "tags" in call_data and call_data["tags"]:
                asyncio.run(lead_service.add_tags_to_lead(lead_id, call_data["tags"]))
        
        logger.info(f"Successfully processed completion for call {call_id}")
        return call
    
    except Exception as e:
        logger.error(f"Error processing completion for call {call_id}: {str(e)}")
        self.retry(exc=e, countdown=2 ** self.request.retries)


@app.task(name='call.analyze_call_transcript', bind=True, max_retries=3)
def analyze_call_transcript(self, call_id: str) -> Dict[str, Any]:
    """
    Analyze a call transcript to extract insights as a background task.
    
    Args:
        call_id: ID of the call
        
    Returns:
        Call data with analysis results
    """
    logger.info(f"Background task: analyzing transcript for call {call_id}")
    
    try:
        # Create service instance
        call_service = create_call_service()
        
        # Convert to awaitable result
        import asyncio
        
        # Get call data
        call = asyncio.run(call_service.get_call(call_id))
        
        if not call:
            logger.error(f"Call {call_id} not found")
            raise ValueError(f"Call {call_id} not found")
        
        # Check if transcript exists
        transcript = call.get("transcript")
        if not transcript or not transcript.get("content"):
            logger.warning(f"No transcript found for call {call_id}")
            return call
        
        # In a real implementation, you would analyze the transcript here
        # For now, we'll just add placeholder analysis results
        
        # Extract key points (placeholder)
        key_points = ["This is a placeholder for key points from the call"]
        
        # Determine sentiment (placeholder)
        sentiment = "neutral"
        
        # Extract action items (placeholder)
        action_items = ["This is a placeholder for action items from the call"]
        
        # Update call metrics with analysis results
        metrics_data = {
            "key_points": key_points,
            "sentiment": sentiment,
            "action_items": action_items,
            "analyzed_at": datetime.now().isoformat()
        }
        
        # Update the call with analysis results
        updated_call = asyncio.run(call_service.update_call(call_id, {"metrics": metrics_data}))
        
        logger.info(f"Successfully analyzed transcript for call {call_id}")
        return updated_call
    
    except Exception as e:
        logger.error(f"Error analyzing transcript for call {call_id}: {str(e)}")
        self.retry(exc=e, countdown=2 ** self.request.retries)


@app.task(name='call.process_call_recording', bind=True, max_retries=3)
def process_call_recording(self, call_id: str, recording_url: str) -> Dict[str, Any]:
    """
    Process a call recording as a background task.
    
    Args:
        call_id: ID of the call
        recording_url: URL of the recording
        
    Returns:
        Dictionary containing processed call details
    """
    logger.info(f"Background task: processing recording for call {call_id}")
    
    try:
        # Create service instance
        call_service = create_call_service()
        
        # Convert to awaitable result
        import asyncio
        result = asyncio.run(call_service.process_call_recording(call_id, recording_url))
        
        # After processing the recording, trigger transcript analysis as a separate task
        analyze_call_transcript.delay(call_id)
        
        logger.info(f"Successfully processed recording for call {call_id}")
        return result
    
    except Exception as e:
        logger.error(f"Error processing recording for call {call_id}: {str(e)}")
        self.retry(exc=e, countdown=2 ** self.request.retries)


@app.task(name='call.schedule_calls_for_campaign', bind=True, max_retries=3)
def schedule_calls_for_campaign(self, campaign_id: str, date_str: str = None, max_calls: int = 50) -> List[Dict[str, Any]]:
    """
    Schedule calls for a campaign on a specific date as a background task.
    
    Args:
        campaign_id: ID of the campaign
        date_str: Date string to schedule calls for (ISO format)
        max_calls: Maximum number of calls to schedule
        
    Returns:
        List of scheduled call data
    """
    logger.info(f"Background task: scheduling calls for campaign {campaign_id}")
    
    try:
        # Create service instances
        call_service = create_call_service()
        lead_service = create_lead_service()
        campaign_service = create_campaign_service()
        
        # Convert to awaitable result
        import asyncio
        
        # Parse date if provided, otherwise use current date
        if date_str:
            date = datetime.fromisoformat(date_str)
        else:
            date = datetime.now()
        
        # Get the campaign details
        campaign = asyncio.run(campaign_service.get_campaign_by_id(campaign_id))
        
        if not campaign:
            logger.error(f"Campaign {campaign_id} not found")
            raise ValueError(f"Campaign {campaign_id} not found")
        
        # Get prioritized leads for the campaign
        leads = asyncio.run(lead_service.get_prioritized_leads(
            gym_id=campaign.get("gym_id"),
            count=max_calls,
            qualification=campaign.get("settings", {}).get("preferred_qualification"),
            exclude_leads=[]  # In a real implementation, exclude leads with scheduled calls
        ))
        
        # Schedule calls for each lead
        scheduled_calls = []
        
        for lead in leads:
            # Create call data
            call_data = {
                "lead_id": lead.get("id"),
                "campaign_id": campaign_id,
                "gym_id": campaign.get("gym_id"),
                "call_status": "scheduled",
                "scheduled_time": date.isoformat()
            }
            
            # Create call
            call = asyncio.run(call_service.trigger_call(
                lead_id=lead.get("id"),
                campaign_id=campaign_id,
                lead_data=lead
            ))
            
            scheduled_calls.append(call)
        
        logger.info(f"Successfully scheduled {len(scheduled_calls)} calls for campaign {campaign_id}")
        return scheduled_calls
    
    except Exception as e:
        logger.error(f"Error scheduling calls for campaign {campaign_id}: {str(e)}")
        self.retry(exc=e, countdown=2 ** self.request.retries) 