"""
Celery task definitions for campaign operations.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, date
import asyncio

from sqlalchemy import text

from backend.celery_app import app
from ...tasks.base import BaseTask
from ...utils.logging.logger import get_logger
from ...db.connections.database import SessionLocal

from .tasks import CampaignSchedulingService
from .campaign_helpers import db_session

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
        if target_date_str:
            try:
                target_date = datetime.fromisoformat(target_date_str).date()
            except ValueError:
                logger.error(f"Invalid date format: {target_date_str}. Using today's date.")
                target_date = date.today()
        else:
            target_date = date.today()
            
        try:
            # Create a fresh event loop that's properly isolated
            old_loop = asyncio.get_event_loop() if asyncio.get_event_loop().is_running() else None
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                # Run our async function and capture the result
                result = loop.run_until_complete(self._schedule_with_shared_session(campaign_id, target_date))
                return result
            finally:
                # Proper cleanup - cancel all pending tasks
                pending_tasks = asyncio.all_tasks(loop)
                for task in pending_tasks:
                    task.cancel()
                
                # Wait for tasks to complete cancellation
                if pending_tasks:
                    loop.run_until_complete(asyncio.gather(*pending_tasks, return_exceptions=True))
                
                # Close the loop completely
                loop.run_until_complete(loop.shutdown_asyncgens())
                loop.close()
                
                # Restore the old loop if there was one
                if old_loop:
                    asyncio.set_event_loop(old_loop)
                
        except Exception as e:
            logger.error(f"Error scheduling calls for campaign {campaign_id}: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            raise self.retry(exc=e, countdown=60 * 5)  # Retry after 5 minutes
    
    async def _schedule_with_shared_session(self, campaign_id: str, target_date: date) -> List[Dict[str, Any]]:
        """Schedule calls using a shared session to prevent connection leaks."""
        session = None
        try:
            # Create a session with explicit autoclose settings
            session = SessionLocal()
            
            # Verify the session connection is working before proceeding
            await session.execute(text("SELECT 1"))
            
            # Import services here to avoid circular imports
            from ...services.campaign.factory import create_campaign_service_async
            from ...services.call.factory import create_call_service_async
            
            # Create services with explicit shared session
            campaign_service = await create_campaign_service_async(session=session)
            call_service = await create_call_service_async(session=session)
            
            # Create service and run the main task operation
            service = self.service_class()
            
            # Execute the scheduling operation with the shared session
            result = await service.schedule_calls_for_campaign(
                campaign_id,
                target_date,
                campaign_service=campaign_service,
                call_service=call_service,
                session=session
            )
            
            # Explicitly commit any pending changes
            await session.commit()
            return result
            
        except Exception as e:
            # Explicitly rollback on errors
            if session:
                await session.rollback()
            logger.error(f"Error in _schedule_with_shared_session: {str(e)}")
            raise
        finally:
            # Always close the session, but with error catching
            if session:
                try:
                    # This is the critical step - we need to explicitly close the session
                    # before the event loop is closed
                    await session.close()
                except Exception as close_error:
                    logger.error(f"Error closing session: {str(close_error)}")


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
        if target_date_str:
            try:
                target_date = datetime.fromisoformat(target_date_str).date()
            except ValueError:
                logger.error(f"Invalid date format: {target_date_str}. Using today's date.")
                target_date = date.today()
        else:
            target_date = date.today()
            
        try:
            # Create a fresh event loop that's properly isolated
            old_loop = asyncio.get_event_loop() if asyncio.get_event_loop().is_running() else None
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                # Run our async function and capture the result
                result = loop.run_until_complete(self._schedule_with_shared_session(target_date))
                return result
            finally:
                # Proper cleanup - cancel all pending tasks
                pending_tasks = asyncio.all_tasks(loop)
                for task in pending_tasks:
                    task.cancel()
                
                # Wait for tasks to complete cancellation
                if pending_tasks:
                    loop.run_until_complete(asyncio.gather(*pending_tasks, return_exceptions=True))
                
                # Close the loop completely
                loop.run_until_complete(loop.shutdown_asyncgens())
                loop.close()
                
                # Restore the old loop if there was one
                if old_loop:
                    asyncio.set_event_loop(old_loop)
                
        except Exception as e:
            logger.error(f"Error scheduling calls for all campaigns: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            raise self.retry(exc=e, countdown=60 * 5)
    
    async def _schedule_with_shared_session(self, target_date: date) -> Dict[str, List[Dict[str, Any]]]:
        """Schedule calls for all campaigns using a shared session."""
        # Create a session directly
        session = SessionLocal()
        
        try:
            # Create services with explicit shared session
            from ...services.campaign.factory import create_campaign_service_async
            campaign_service = await create_campaign_service_async(session=session)
            
            # Create service and run the operation
            service = self.service_class()
            
            # Execute the scheduling operation with the shared session
            return await service.schedule_calls_for_all_campaigns(
                target_date,
                get_session=lambda: session  # Pass a function that returns the session
            )
        finally:
            # Make sure to close the session no matter what
            await session.close()


# Create and register tasks with Celery
schedule_campaign_task = app.register_task(ScheduleCampaignTask())
schedule_all_campaigns_task = app.register_task(ScheduleAllCampaignsTask())
