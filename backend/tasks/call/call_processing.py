"""
Call processing tasks for complex operations.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from ...services.call.interface import CallService
from ...services.lead.interface import LeadService
from ...services.campaign.interface import CampaignService
from ...utils.logging.logger import get_logger

logger = get_logger(__name__)

async def process_call_completion(
    call_service: CallService,
    lead_service: LeadService,
    call_id: str,
    call_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Process a call after it has been completed.
    
    Args:
        call_service: Call service instance
        lead_service: Lead service instance
        call_id: ID of the call
        call_data: Call data including outcome, notes, etc.
        
    Returns:
        Updated call data
    """
    logger.info(f"Processing call {call_id} completion")
    
    # Update call with completion data
    call = await call_service.update_call(call_id, {
        "status": "completed",
        "end_time": datetime.now(),
        "outcome": call_data.get("outcome"),
        "notes": call_data.get("notes")
    })
    
    if not call:
        logger.error(f"Call {call_id} not found")
        raise ValueError(f"Call {call_id} not found")
    
    # Update lead based on call outcome
    lead_id = call.get("lead_id")
    if lead_id:
        logger.info(f"Updating lead {lead_id} based on call outcome")
        
        # Prepare lead update data
        lead_update_data = {
            "last_call_date": datetime.now()
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
        await lead_service.update_lead(lead_id, lead_update_data)
        
        # Update lead qualification if needed
        if "qualification" in call_data:
            await lead_service.qualify_lead(lead_id, call_data["qualification"])
        
        # Add tags if provided
        if "tags" in call_data and call_data["tags"]:
            await lead_service.add_tags_to_lead(lead_id, call_data["tags"])
    
    logger.info(f"Completed processing for call {call_id}")
    return call

async def analyze_call_transcript(
    call_service: CallService,
    call_id: str
) -> Dict[str, Any]:
    """
    Analyze a call transcript to extract insights.
    
    Args:
        call_service: Call service instance
        call_id: ID of the call
        
    Returns:
        Call data with analysis results
    """
    logger.info(f"Analyzing transcript for call {call_id}")
    
    # Get call data
    call = await call_service.get_call_by_id(call_id)
    
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
        "analyzed_at": datetime.now()
    }
    
    updated_call = await call_service.update_call_metrics(call_id, metrics_data)
    
    logger.info(f"Completed transcript analysis for call {call_id}")
    return updated_call

async def schedule_calls_for_campaign(
    call_service: CallService,
    lead_service: LeadService,
    campaign_service: CampaignService,
    campaign_id: str,
    date: datetime,
    max_calls: int = 50
) -> List[Dict[str, Any]]:
    """
    Schedule calls for a campaign on a specific date.
    
    Args:
        call_service: Call service instance
        lead_service: Lead service instance
        campaign_service: Campaign service instance
        campaign_id: ID of the campaign
        date: Date to schedule calls for
        max_calls: Maximum number of calls to schedule
        
    Returns:
        List of scheduled call data
    """
    logger.info(f"Scheduling calls for campaign {campaign_id} on {date}")
    
    # Get campaign details
    campaign = await campaign_service.get_campaign_by_id(campaign_id)
    
    if not campaign:
        logger.error(f"Campaign {campaign_id} not found")
        raise ValueError(f"Campaign {campaign_id} not found")
    
    # Get prioritized leads for the campaign
    leads = await lead_service.get_prioritized_leads(
        gym_id=campaign.get("gym_id"),
        count=max_calls,
        qualification=campaign.get("settings", {}).get("preferred_qualification"),
        exclude_leads=[]  # In a real implementation, you would exclude leads that already have calls scheduled
    )
    
    # Schedule calls for each lead
    scheduled_calls = []
    
    # Get campaign schedule for the day
    schedule = campaign.get("schedule", {}).get(date.strftime("%A").lower(), {})
    start_hour = schedule.get("start_hour", 9)
    end_hour = schedule.get("end_hour", 17)
    call_duration_minutes = schedule.get("call_duration_minutes", 15)
    
    # Calculate available time slots
    available_slots = []
    current_time = datetime.combine(date.date(), datetime.min.time().replace(hour=start_hour))
    end_time = datetime.combine(date.date(), datetime.min.time().replace(hour=end_hour))
    
    while current_time < end_time:
        available_slots.append(current_time)
        current_time += timedelta(minutes=call_duration_minutes)
    
    # Schedule calls for each lead
    for i, lead in enumerate(leads):
        if i >= len(available_slots):
            break
        
        # Create call record
        call_data = {
            "lead_id": lead.get("id"),
            "campaign_id": campaign_id,
            "gym_id": campaign.get("gym_id"),
            "status": "scheduled",
            "scheduled_time": available_slots[i],
            "created_at": datetime.now()
        }
        
        call = await call_service.create_call(call_data)
        scheduled_calls.append(call)
    
    logger.info(f"Scheduled {len(scheduled_calls)} calls for campaign {campaign_id}")
    return scheduled_calls

async def generate_call_reports(
    call_service: CallService,
    gym_id: str,
    start_date: datetime,
    end_date: datetime
) -> Dict[str, Any]:
    """
    Generate reports on calls for a specific period.
    
    Args:
        call_service: Call service instance
        gym_id: ID of the gym
        start_date: Start date for the report
        end_date: End date for the report
        
    Returns:
        Report data
    """
    logger.info(f"Generating call reports for gym {gym_id} from {start_date} to {end_date}")
    
    # Get all calls for the period
    calls_result = await call_service.get_calls_by_date_range(gym_id, start_date, end_date)
    calls = calls_result.get("calls", [])
    
    # Calculate metrics
    total_calls = len(calls)
    completed_calls = sum(1 for call in calls if call.get("status") == "completed")
    scheduled_calls = sum(1 for call in calls if call.get("status") == "scheduled")
    failed_calls = sum(1 for call in calls if call.get("status") == "failed")
    
    # Calculate outcome distribution
    outcome_counts = {}
    for call in calls:
        outcome = call.get("outcome")
        if outcome:
            outcome_counts[outcome] = outcome_counts.get(outcome, 0) + 1
    
    # Calculate average call duration
    durations = [call.get("metrics", {}).get("duration", 0) for call in calls if call.get("status") == "completed"]
    avg_duration = sum(durations) / len(durations) if durations else 0
    
    # Generate report
    report = {
        "gym_id": gym_id,
        "start_date": start_date,
        "end_date": end_date,
        "total_calls": total_calls,
        "completed_calls": completed_calls,
        "scheduled_calls": scheduled_calls,
        "failed_calls": failed_calls,
        "completion_rate": (completed_calls / total_calls) if total_calls > 0 else 0,
        "outcome_distribution": outcome_counts,
        "average_duration": avg_duration,
        "generated_at": datetime.now()
    }
    
    logger.info(f"Generated call reports for gym {gym_id}")
    return report 