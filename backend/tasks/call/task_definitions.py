"""
Task definitions for call-related operations.
"""
from typing import Optional
import uuid
from datetime import datetime

from backend.celery_app import app
from backend.services.call.factory import create_call_service
from backend.utils.logging.logger import get_logger

logger = get_logger(__name__)

@app.task(name='call.trigger_call', queue='call_tasks')
def trigger_call_task(lead_id: str, campaign_id: Optional[str] = None):
    """
    Task to trigger a call to a lead.
    
    Args:
        lead_id: ID of the lead to call
        campaign_id: Optional ID of the campaign
    """
    logger.info(f"Triggering call to lead {lead_id} for campaign {campaign_id or 'N/A'}")
    
    # Create call service
    call_service = create_call_service()
    
    # Convert string IDs to UUIDs
    lead_uuid = uuid.UUID(lead_id)
    campaign_uuid = uuid.UUID(campaign_id) if campaign_id else None
    
    # Trigger the call
    try:
        result = call_service.trigger_call(lead_uuid, campaign_uuid)
        logger.info(f"Call triggered successfully: {result}")
        return result
    except Exception as e:
        logger.error(f"Error triggering call: {str(e)}")
        raise

