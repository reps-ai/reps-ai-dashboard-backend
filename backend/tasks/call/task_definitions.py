"""
Task definitions for call-related operations.
"""
from typing import Optional, Dict, Any
import uuid
import asyncio
import os
from datetime import datetime

from backend.celery_app import app
from backend.services.call.factory import create_call_service_async
from backend.utils.logging.logger import get_logger

logger = get_logger(__name__)

@app.task(name='call.trigger_call', queue='call_tasks')
def trigger_call_task(lead_id: str, campaign_id: Optional[str] = None):
    """
    Trigger a call to a lead.
    
    Args:
        lead_id: ID of the lead to call
        campaign_id: Optional campaign ID
    
    Returns:
        Dict with call result details
    """
    logger.info(f"Triggering call for lead {lead_id} from campaign {campaign_id}")
    
    # Check for Retell API key before even trying to create the service
    has_retell_api_key = bool(os.environ.get('RETELL_API_KEY'))
    if not has_retell_api_key:
        logger.warning("RETELL_API_KEY not found in environment variables. Call will be created in 'pending' status.")
    
    # Run in async context
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        async def _trigger_call():
            # Create appropriate call service config based on API key availability
            service_config = {"enable_retell": has_retell_api_key}
            
            # Create call service
            call_service = await create_call_service_async(config=service_config)
            
            # Trigger the call
            result = await call_service.trigger_call(
                lead_id=uuid.UUID(lead_id),
                campaign_id=uuid.UUID(campaign_id) if campaign_id else None
            )
            
            return result
            
        # Run the async function
        result = loop.run_until_complete(_trigger_call())
        logger.info(f"Successfully triggered call for lead {lead_id}")
        return result
        
    except Exception as e:
        logger.error(f"Error triggering call for lead {lead_id}: {str(e)}")
        raise
    finally:
        # Clean up
        loop.close()

# Additional call tasks can be added below
# For example:
# @app.task(name='call.process_recording', queue='call_tasks')
# def process_call_recording(call_id: str, recording_url: str):
#     """Process a call recording."""
#     # Implementation

