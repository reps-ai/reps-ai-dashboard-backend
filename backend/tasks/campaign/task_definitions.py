"""
Celery task definitions for campaign operations.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, date
import asyncio

from backend.celery_app import app
from ...tasks.base import BaseTask
from ...utils.logging.logger import get_logger
from asgiref.sync import async_to_sync

from .tasks import CampaignSchedulingService

# Task constants
TASK_MAX_RETRIES = 3
TASK_DEFAULT_QUEUE = 'campaign_tasks'

# Configure logging
logger = get_logger(__name__)


class ScheduleCampaignTask(BaseTask):
    """Task to schedule calls for a specific campaign."""
    
    name = "campaign.schedule_campaign"
    max_retries = TASK_MAX_RETRIES
    queue = TASK_DEFAULT_QUEUE
    service_class = CampaignSchedulingService
    
    def run(self, campaign_id: str, target_date_str: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Schedule calls for a campaign on a specific date.
        
        Args:
            campaign_id: ID of the campaign
            target_date_str: Date to schedule calls for in ISO format (defaults to today)
            
        Returns:
            List of scheduled calls
        """
        logger.info(f"Scheduling calls for campaign {campaign_id} on {target_date_str or 'today'}")
        
        # Convert string date to date object if provided
        target_date = None
        if target_date_str:
            try:
                target_date = datetime.fromisoformat(target_date_str).date()
            except ValueError:
                logger.error(f"Invalid date format: {target_date_str}. Using today's date.")
                target_date = date.today()
        else:
            target_date = date.today()
            
        try:
            # Get service instance
            service = self.get_service()
            
            # Use async_to_sync to run the async function in a sync context
            result = async_to_sync(lambda: service.schedule_calls_for_campaign(campaign_id, target_date))()
            return result
            
        except Exception as e:
            logger.error(f"Error scheduling calls for campaign {campaign_id}: {str(e)}")
            raise self.retry(exc=e, countdown=60 * 5)  # Retry after 5 minutes


class ScheduleAllCampaignsTask(BaseTask):
    """Task to schedule calls for all active campaigns."""
    
    name = "campaign.schedule_all_campaigns"
    max_retries = TASK_MAX_RETRIES
    queue = TASK_DEFAULT_QUEUE
    service_class = CampaignSchedulingService
    
    def run(self, target_date_str: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        Schedule calls for all active campaigns on a specific date.
        
        Args:
            target_date_str: Date to schedule calls for in ISO format (defaults to today)
            
        Returns:
            Dictionary mapping campaign IDs to lists of scheduled calls
        """
        logger.info(f"Scheduling calls for all campaigns on {target_date_str or 'today'}")
        
        # Convert string date to date object if provided
        target_date = None
        if target_date_str:
            try:
                target_date = datetime.fromisoformat(target_date_str).date()
            except ValueError:
                logger.error(f"Invalid date format: {target_date_str}. Using today's date.")
                target_date = date.today()
        else:
            target_date = date.today()
            
        try:
            # Get service instance
            service = self.get_service()
            
            # Use async_to_sync to run the async function in a sync context
            result = async_to_sync(lambda: service.schedule_calls_for_all_campaigns(target_date))()
            return result
            
        except Exception as e:
            logger.error(f"Error scheduling calls for all campaigns: {str(e)}")
            raise self.retry(exc=e, countdown=60 * 5)  # Retry after 5 minutes


# Create and register tasks with Celery
schedule_campaign_task = app.register_task(ScheduleCampaignTask())
schedule_all_campaigns_task = app.register_task(ScheduleAllCampaignsTask())
