"""
Lead prioritization utilities for campaign scheduling.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, date
from ...utils.logging.logger import get_logger

# Configure logging
logger = get_logger(__name__)

async def get_lead_last_call_outcome(call_service, lead_id: str) -> Optional[str]:
    """
    Get the last call outcome for a lead from call logs.
    
    Args:
        call_service: Call service instance
        lead_id: Lead ID
            
    Returns:
        Last call outcome or None if no calls found
    """
    try:
        # Get the most recent call for this lead - ordered by date descending
        calls = await call_service.get_calls_by_lead(lead_id, page=1, page_size=1)
        
        if calls and len(calls) > 0:
            # Return the outcome of the most recent call from the outcome column
            return calls[0].get('outcome')
        
        return None
    except Exception as e:
        logger.error(f"Error getting last call outcome for lead {lead_id}: {str(e)}")
        return None

def prioritize_leads(leads: List[Dict[str, Any]], gap_days: int, call_outcomes: Dict[str, str]) -> List[Dict[str, Any]]:
    """
    Prioritize leads based on their status and history.
    
    Args:
        leads: List of leads to prioritize
        gap_days: Minimum gap between calls in days
        call_outcomes: Dictionary mapping lead_id to last call outcome
        
    Returns:
        List of prioritized leads
    """
    # First, filter out "not interested" leads and already converted leads
    filtered_leads = []
    
    for lead in leads:
        lead_status = lead.get('lead_status')  # Using lead_status instead of status
        lead_id = str(lead.get('id'))
        last_outcome = call_outcomes.get(lead_id)
        
        # Skip converted leads and leads that expressed they're not interested
        if lead_status == 'converted' or last_outcome == 'not_interested':
            continue
            
        filtered_leads.append(lead)
    
    if not filtered_leads:
        return []
    
    # Priority 1: New leads
    new_leads = [lead for lead in filtered_leads if lead.get('lead_status') == 'new']  # Using lead_status instead of status
    
    # Priority 2: Contacted leads that haven't been contacted in 'gap_days'
    contacted_leads = []
    for lead in filtered_leads:
        if lead in new_leads:
            continue
            
        last_called = lead.get('last_called')  # Using last_called instead of last_contacted
        
        if last_called:
            if isinstance(last_called, str):
                last_called_date = datetime.fromisoformat(last_called.replace('Z', '+00:00')).date()
            else:
                last_called_date = last_called.date() if isinstance(last_called, datetime) else last_called
            
            next_contact_date = last_called_date + timedelta(days=gap_days)
            
            if date.today() >= next_contact_date:
                contacted_leads.append(lead)
    
    # Priority 3: Any remaining leads that passed our initial filter
    remaining_leads = [lead for lead in filtered_leads if lead not in new_leads and lead not in contacted_leads]
    
    return new_leads + contacted_leads + remaining_leads
