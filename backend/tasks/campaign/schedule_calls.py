"""
Task for scheduling calls for campaigns.
"""
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, date, time, timedelta
from sqlalchemy import select, and_, or_
from contextlib import asynccontextmanager

from backend.celery_app import app
from backend.db.connections.database import get_db
from backend.db.models.campaign.follow_up_campaign import FollowUpCampaign
from backend.services.call.factory import create_call_service
from backend.services.campaign.factory import create_campaign_service
from backend.utils.logging.logger import get_logger
from asgiref.sync import async_to_sync

# Configure proper logging
logger = get_logger(__name__)

# Task constants
TASK_MAX_RETRIES = 3
TASK_DEFAULT_QUEUE = 'campaign_tasks'
CALL_HOURS_START = time(18, 0)  # 6 PM
CALL_HOURS_END = time(21, 0)    # 9 PM

# Create a proper async context manager from the get_db generator
@asynccontextmanager
async def db_session():
    """
    Context manager to properly handle the database session.
    """
    db_gen = get_db()
    try:
        session = await db_gen.__anext__()
        yield session
    finally:
        try:
            await db_gen.__anext__()
        except StopAsyncIteration:
            pass

@app.task(
    name='campaign.schedule_campaign',
    bind=True,
    max_retries=TASK_MAX_RETRIES,
    queue=TASK_DEFAULT_QUEUE  # This is 'campaign_tasks'
)
def schedule_campaign_task(self, campaign_id: str, target_date_str: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Celery task to schedule calls for a campaign on a specific date.
    
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
        # Use async_to_sync to run the async function in a sync context
        return async_to_sync(lambda: schedule_calls_for_campaign(campaign_id, target_date))()
        
    except Exception as e:
        logger.error(f"Error scheduling calls for campaign {campaign_id}: {str(e)}")
        raise self.retry(exc=e, countdown=60 * 5)  # Retry after 5 minutes

@app.task(
    name='campaign.schedule_all_campaigns',
    bind=True,
    max_retries=TASK_MAX_RETRIES,
    queue=TASK_DEFAULT_QUEUE
)
def schedule_all_campaigns_task(self, target_date_str: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
    """
    Celery task to schedule calls for all active campaigns on a specific date.
    
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
        # Use async_to_sync to run the async function in a sync context
        from asgiref.sync import async_to_sync
        return async_to_sync(schedule_calls_for_all_campaigns)(target_date)
    except Exception as e:
        logger.error(f"Error scheduling calls for all campaigns: {str(e)}")
        raise self.retry(exc=e, countdown=60 * 5)  # Retry after 5 minutes

async def schedule_calls_for_campaign(
    campaign_id: str, 
    target_date: Optional[date] = None,
    get_session=None
) -> List[Dict[str, Any]]:
    """
    Schedule calls for a campaign on a specific date.
    
    Args:
        campaign_id: ID of the campaign
        target_date: Date to schedule calls for (defaults to today)
        get_session: Function to provide a database session
        
    Returns:
        List of scheduled calls
    """
    if target_date is None:
        target_date = date.today()
        
    logger.info(f"Scheduling calls for campaign {campaign_id} on {target_date}")
    
    # Use the provided session factory or fall back to our custom db_session context manager
    if get_session is None:
        get_session = db_session
    
    async with get_session() as session:
        # Create service instances with proper repositories
        from backend.services.campaign.factory import create_campaign_service_async
        from backend.services.call.factory import create_call_service_async
        
        campaign_service = await create_campaign_service_async()
        call_service = await create_call_service_async()
        
        # 1. Get the campaign details
        campaign = await campaign_service.get_campaign(campaign_id)
        if not campaign:
            logger.error(f"Campaign {campaign_id} not found")
            return []
        
        # Check if campaign is active based on date range
        campaign_start_date = campaign.get('start_date')
        campaign_end_date = campaign.get('end_date')
        current_date = datetime.now().date()
        
        # Convert datetime objects to date for comparison
        if campaign_start_date and isinstance(campaign_start_date, datetime):
            campaign_start_date = campaign_start_date.date()
        if campaign_end_date and isinstance(campaign_end_date, datetime):
            campaign_end_date = campaign_end_date.date()
        
        is_active = True
        if campaign_start_date and current_date < campaign_start_date:
            is_active = False
        if campaign_end_date and current_date > campaign_end_date:
            is_active = False
            
        # Skip if campaign is not active based on date range
        if not is_active:
            logger.info(f"Campaign {campaign_id} is not active (outside date range), skipping scheduling")
            return []
        
        # 2. Check if the target date is within the campaign date range
        schedule = campaign.get('schedule', {})
        start_date = schedule.get('start_date') or campaign_start_date
        end_date = schedule.get('end_date') or campaign_end_date
        
        # Convert datetime objects to date for comparison
        if start_date and isinstance(start_date, datetime):
            start_date = start_date.date()
        if end_date and isinstance(end_date, datetime):
            end_date = end_date.date()
        
        if start_date and target_date < start_date:
            logger.info(f"Target date {target_date} is before campaign start date {start_date}, skipping")
            return []
            
        if end_date and target_date > end_date:
            logger.info(f"Target date {target_date} is after campaign end date {end_date}, skipping")
            return []
        
        # 3. Check if the target day is a valid call day for the campaign
        weekday = target_date.strftime('%a').lower()
        call_days = schedule.get('call_days', [])
        
        if call_days and weekday not in call_days:
            logger.info(f"Target day {weekday} is not in allowed call days: {call_days}, skipping")
            return []
        
        # 4. Get the number of calls to schedule based on frequency
        frequency = campaign.get('frequency', 0)
        if frequency <= 0:
            logger.info(f"Campaign {campaign_id} has frequency set to {frequency}, skipping")
            return []
        
        # Check if we've already reached the maximum number of calls for this campaign
        # Use call_count field directly from the campaign data
        call_count = campaign.get('call_count', 0)
        
        if call_count >= frequency:
            logger.info(f"Campaign {campaign_id} has already reached its maximum number of calls ({frequency}), marking as completed")
            await campaign_service.update_campaign(campaign_id, {'end_date': current_date})
            return []
        
        # Calculate how many calls to schedule today
        remaining_calls = frequency - call_count
        max_daily_calls = schedule.get('max_daily_calls', 10)  # Default to 10 calls per day
        calls_to_schedule = min(remaining_calls, max_daily_calls)
        
        # 5. Get prioritized leads for the campaign
        # First get all leads associated with the campaign
        campaign_leads = await campaign_service.get_campaign_leads(campaign_id)
        
        lead_ids = [lead.get('lead_id') for lead in campaign_leads]
        if not lead_ids:
            logger.info(f"No leads found for campaign {campaign_id}, skipping")
            return []
        
        # Get detailed lead data for prioritization
        # Create lead service using the proper factory method
        from backend.services.lead.factory import LeadServiceFactory
        lead_service = await LeadServiceFactory.create_service(session)
        
        leads = []
        for lead_id in lead_ids:
            try:
                lead = await lead_service.get_lead(lead_id)
                if lead:
                    leads.append(lead)
            except Exception as e:
                logger.error(f"Error retrieving lead {lead_id}: {str(e)}")
        
        today_calls = await call_service.get_calls_by_date_range(
            campaign.get('branch_id'),
            datetime.combine(target_date, datetime.min.time()),
            datetime.combine(target_date, datetime.max.time())
        )
        
        today_lead_ids = [call.get('lead_id') for call in today_calls]
        leads = [lead for lead in leads if lead.get('id') not in today_lead_ids]
        
        prioritized_leads = []
        
        new_leads = [lead for lead in leads if lead.get('status') == 'new']
        prioritized_leads.extend(new_leads)
        
        gap_days = campaign.get('gap', 7)
        converted_leads = []
        for lead in leads:
            if lead in prioritized_leads:
                continue
                
            last_contacted = lead.get('last_contacted')
            status = lead.get('status')
            
            if last_contacted and status == 'converted':
                last_contact_date = datetime.fromisoformat(last_contacted.replace('Z', '+00:00')).date()
                next_contact_date = last_contact_date + timedelta(days=gap_days)
                
                if target_date >= next_contact_date:
                    converted_leads.append(lead)
        
        prioritized_leads.extend(converted_leads)
        
        low_priority_leads = []
        for lead in leads:
            if lead in prioritized_leads:
                continue
                
            outcome = lead.get('last_outcome')
            status = lead.get('status')
            
            if outcome == 'not_interested' or status == 'converted':
                low_priority_leads.append(lead)
        
        prioritized_leads.extend(low_priority_leads)
        
        for lead in leads:
            if lead not in prioritized_leads:
                prioritized_leads.append(lead)
        
        prioritized_leads = prioritized_leads[:calls_to_schedule]
        
        scheduled_calls = []
        
        call_date_start = datetime.combine(target_date, CALL_HOURS_START)
        call_date_end = datetime.combine(target_date, CALL_HOURS_END)
        
        call_duration_minutes = 10
        available_slots = []
        
        current_time = call_date_start
        while current_time + timedelta(minutes=call_duration_minutes) <= call_date_end:
            available_slots.append(current_time)
            current_time += timedelta(minutes=call_duration_minutes)
        
        for i, lead in enumerate(prioritized_leads):
            if i >= len(available_slots):
                break
                
            try:
                from backend.tasks.call.task_definitions import trigger_call_task
                
                scheduled_time = available_slots[i]
                eta = scheduled_time
                
                trigger_call_task.apply_async(
                    args=[str(lead.get('id')), str(campaign_id)],
                    eta=eta
                )
                
                scheduled_calls.append({
                    'lead_id': lead.get('id'),
                    'campaign_id': campaign_id,
                    'scheduled_time': scheduled_time.isoformat(),
                    'status': 'scheduled'
                })
                
                logger.info(f"Scheduled call to lead {lead.get('id')} for campaign {campaign_id} at {scheduled_time}")
            except Exception as e:
                logger.error(f"Error scheduling call for lead {lead.get('id')}: {str(e)}")
        
        # After scheduling calls, update call count
        new_call_count = call_count + len(scheduled_calls)
        
        # Update campaign metrics and call count
        metrics = campaign.get('metrics', {})
        metrics['scheduled_calls'] = metrics.get('scheduled_calls', 0) + len(scheduled_calls)
        metrics['last_scheduled_date'] = target_date.isoformat()
        
        await campaign_service.update_campaign(campaign_id, {
            'metrics': metrics,
            'call_count': new_call_count
        })
        
        # If we've scheduled all the required calls, mark the campaign as complete
        if new_call_count >= frequency:
            logger.info(f"Campaign {campaign_id} has reached its target frequency, marking as inactive")
            await campaign_service.update_campaign(campaign_id, {'end_date': current_date})
        
        logger.info(f"Scheduled {len(scheduled_calls)} calls for campaign {campaign_id}")
        return scheduled_calls

async def schedule_calls_for_all_campaigns(target_date: Optional[date] = None) -> Dict[str, List[Dict[str, Any]]]:
    """
    Schedule calls for all active campaigns on a specific date.
    
    Args:
        target_date: Date to schedule calls for (defaults to today)
        
    Returns:
        Dictionary mapping campaign IDs to lists of scheduled calls
    """
    if target_date is None:
        target_date = date.today()
        
    logger.info(f"Scheduling calls for all active campaigns on {target_date}")
    
    # Use our new db_session context manager instead of get_db directly
    async with db_session() as session:
        campaign_service = create_campaign_service()
        
        try:
            current_date = datetime.now().date()
            
            query = select(FollowUpCampaign).where(
                and_(
                    or_(
                        FollowUpCampaign.start_date == None,
                        FollowUpCampaign.start_date <= current_date
                    ),
                    or_(
                        FollowUpCampaign.end_date == None,
                        FollowUpCampaign.end_date >= current_date
                    )
                )
            )
            
            result = await session.execute(query)
            active_campaigns = result.scalars().all()
            
            if not active_campaigns:
                logger.info("No active campaigns found")
                return {}
                
            logger.info(f"Found {len(active_campaigns)} active campaigns")
            
            results = {}
            for campaign in active_campaigns:
                try:
                    campaign_id = str(campaign.id)
                    scheduled_calls = await schedule_calls_for_campaign(campaign_id, target_date)
                    results[campaign_id] = scheduled_calls
                except Exception as e:
                    logger.error(f"Error scheduling calls for campaign {campaign.id}: {str(e)}")
            
            return results
        except Exception as e:
            logger.error(f"Error retrieving active campaigns: {str(e)}")
            return {}