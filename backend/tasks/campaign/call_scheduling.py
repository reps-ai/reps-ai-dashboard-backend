"""
Call scheduling utilities for campaign tasks.
"""
from typing import Dict, Any, List
from datetime import datetime, date, time, timedelta
from ...utils.logging.logger import get_logger

# Configure logging
logger = get_logger(__name__)

async def create_scheduled_calls(
    prioritized_leads: List[Dict[str, Any]], 
    campaign_id: str, 
    target_date: date,
    start_time: time,
    end_time: time
) -> List[Dict[str, Any]]:
    """
    Create scheduled calls for the prioritized leads.
    
    Args:
        prioritized_leads: List of prioritized leads
        campaign_id: Campaign ID
        target_date: Date to schedule calls for
        start_time: Start time for calls
        end_time: End time for calls
        
    Returns:
        List of scheduled calls
    """
    scheduled_calls = []
    
    call_date_start = datetime.combine(target_date, start_time)
    call_date_end = datetime.combine(target_date, end_time)
    
    call_duration_minutes = 10  # Each call takes 10 minutes
    available_slots = []
    
    # Generate time slots
    current_time = call_date_start
    while current_time + timedelta(minutes=call_duration_minutes) <= call_date_end:
        available_slots.append(current_time)
        current_time += timedelta(minutes=call_duration_minutes)
    
    # Schedule calls for each lead
    for i, lead in enumerate(prioritized_leads):
        if i >= len(available_slots):
            break
            
        try:
            from ..call.task_definitions import trigger_call_task
            
            scheduled_time = available_slots[i]
            eta = scheduled_time
            
            # This is where the magic happens - the call is triggered at the specific time (eta)
            # using Celery's delayed task execution 
            task = trigger_call_task.apply_async(
                args=[str(lead.get('id')), str(campaign_id)],
                eta=eta
            )
            
            scheduled_calls.append({
                'lead_id': lead.get('id'),
                'campaign_id': campaign_id,
                'scheduled_time': scheduled_time.isoformat(),
                'status': 'scheduled',
                'task_id': task.id  # Store the Celery task ID for task tracking/revocation
            })
            
            logger.info(f"Scheduled call to lead {lead.get('id')} for campaign {campaign_id} at {scheduled_time} (task ID: {task.id})")
        except Exception as e:
            logger.error(f"Error scheduling call for lead {lead.get('id')}: {str(e)}")
    
    return scheduled_calls
