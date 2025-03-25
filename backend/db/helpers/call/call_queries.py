"""
Database helper functions for call-related operations.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy import select, and_, or_, func, desc, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.call.call_log import CallLog
from ...models.lead import Lead
from ...models.campaign.follow_up_campaign import FollowUpCampaign
from ...models.call.follow_up_call import FollowUpCall
from ...models.user import User
from ...models.gym.branch import Branch
from ...models.gym.gym import Gym
from ....utils.logging.logger import get_logger


logger = get_logger(__name__)

async def get_call_with_related_data(session: AsyncSession, call_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a call with all related data.
    
    Args:
        session: Database session
        call_id: Call ID
        
    Returns:
        Call data with related information or None if not found
    """
    # Get call using unique().scalar() for better 1.4 compatibility
    call_query = select(CallLog).where(CallLog.id == call_id)
    result = await session.execute(call_query)
    call = result.unique().scalar_one_or_none()
    
    if not call:
        return None
    
    call_dict = call.to_dict()
    
    # Use explicit joins for better compatibility
    if call.lead_id:
        lead_query = (
            select(Lead)
            .join(CallLog, CallLog.lead_id == Lead.id)
            .where(Lead.id == call.lead_id)
        )
        lead_result = await session.execute(lead_query)
        lead = lead_result.unique().scalar_one_or_none()
        if lead:
            call_dict["lead"] = {
                "id": lead.id,
                "first_name": lead.first_name,
                "last_name": lead.last_name,
                "phone": lead.phone,
                "email": lead.email,
                "lead_status": lead.lead_status
            }
    
    # Get campaign information if applicable
    if call.campaign_id:
        campaign_query = select(FollowUpCampaign).where(FollowUpCampaign.id == call.campaign_id)
        campaign_result = await session.execute(campaign_query)
        campaign = campaign_result.scalar_one_or_none()
        if campaign:
            call_dict["campaign"] = {
                "id": campaign.id,
                "name": campaign.name
            }

    # Get branch and gym information if applicable
    if call.branch_id:
        branch_query = select(Branch).where(Branch.id == call.branch_id)
        branch_result = await session.execute(branch_query)
        branch = branch_result.scalar_one_or_none()
        if branch:
            call_dict["branch"] = {
                "id": branch.id,
                "name": branch.name
            }
    
    if call.gym_id:
        gym_query = select(Gym).where(Gym.id == call.gym_id)
        gym_result = await session.execute(gym_query)
        gym = gym_result.scalar_one_or_none()
        if gym:
            call_dict["gym"] = {
                "id": gym.id,
                "name": gym.name
            }
    
    return call_dict

async def get_calls_by_campaign_db(
    session: AsyncSession,
    campaign_id: str,
    page: int = 1,
    page_size: int = 50,
    sort_by: str = "start_time",  # Field to sort by; default is "start_time"
    sort_order: str = "desc"  # Order of sorting; default is "desc"
    
) -> Dict[str, Any]:
    """
    Get all calls for a campaign with pagination.
    
    Args:
        session: Database session
        campaign_id: Campaign ID
        page: Page number
        page_size: Page size
        sort_by: Field to sort by
        sort_order: Order of sorting
        
    Returns:
        Dictionary containing calls and pagination info
    """
    # Get calls for the campaign directly from CallLog
    base_query = select(CallLog).where(CallLog.campaign_id == campaign_id)

     # Apply sorting: try to get the sort column from CallLog;
    # if not found, default to CallLog.start_time
    sort_column = getattr(CallLog, sort_by, CallLog.start_time)
    if sort_order.lower() == "asc":
        base_query = base_query.order_by(sort_column.asc())
    else:
        base_query = base_query.order_by(sort_column.desc())
    
    
    # Count total calls
    count_query = select(func.count()).select_from(base_query.subquery())
    total_count = await session.execute(count_query)
    total = total_count.scalar_one()
    
    if total == 0:
        return {
            "calls": [],
            "pagination": {
                "total": 0,
                "page": page,
                "page_size": page_size,
                "pages": 0
            }
        }
    
    # Get calls with pagination
    offset = (page - 1) * page_size
    calls_query = base_query.offset(offset).limit(page_size)
    calls_result = await session.execute(calls_query)
    calls = calls_result.scalars().all()
    
    # Get full call data
    call_data = []
    for call in calls:
        call_data.append(await get_call_with_related_data(session, call.id))
    
    return {
        "calls": call_data,
        "pagination": {
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": (total + page_size - 1) // page_size
        }
    }

async def get_calls_by_lead_db(
    session: AsyncSession,
    lead_id: str,
    page: int = 1,
    page_size: int = 50,
    sort_by: str = "start_time",  # Field to sort by; default is "start_time"
    sort_order: str = "desc"  # Order of sorting; default is "desc"
) -> Dict[str, Any]:
    """
    Get all calls for a lead with pagination.
    
    Args:
        session: Database session
        lead_id: Lead ID
        page: Page number
        page_size: Page size
        sort_by: Field to sort by
        sort_order: Order of sorting
        
    Returns:
        Dictionary containing calls and pagination info
    """
    # Get calls for the lead directly from CallLog
    base_query = select(CallLog).where(CallLog.lead_id == lead_id)

    # Apply sorting: try to get the sort column from CallLog;
    # if not found, default to CallLog.start_time
    sort_column = getattr(CallLog, sort_by, CallLog.start_time)
    if sort_order.lower() == "asc":
        base_query = base_query.order_by(sort_column.asc())
    else:
        base_query = base_query.order_by(sort_column.desc())
    
    # Count total calls
    count_query = select(func.count()).select_from(base_query.subquery())
    total_count = await session.execute(count_query)
    total = total_count.scalar_one()
    
    if total == 0:
        return {
            "calls": [],
            "pagination": {
                "total": 0,
                "page": page,
                "page_size": page_size,
                "pages": 0
            }
        }
    
    # Get calls with pagination
    offset = (page - 1) * page_size
    calls_query = base_query.offset(offset).limit(page_size)
    calls_result = await session.execute(calls_query)
    calls = calls_result.scalars().all()
    
    # Get full call data
    call_data = []
    for call in calls:
        call_data.append(await get_call_with_related_data(session, call.id))
    
    return {
        "calls": call_data,
        "pagination": {
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": (total + page_size - 1) // page_size
        }
    }

async def get_calls_by_date_range_db(
    session: AsyncSession,
    gym_id: str,
    start_date: datetime,
    end_date: datetime,
    page: int = 1,
    page_size: int = 50,
    sort_order: str = "desc"  # Order of sorting; default is "desc"
) -> Dict[str, Any]:
    """
    Get calls within a date range with pagination.
    
    Args:
        session: Database session
        gym_id: Gym ID (branch_id)
        start_date: Start of the date range
        end_date: End of the date range
        page: Page number
        page_size: Page size
        sort_order: Order of sorting
        
    Returns:
        Dictionary containing calls and pagination info
    """
    # First, get branch IDs for the gym
    branch_query = select(Branch.gym_id).where(Branch.gym_id == gym_id)#TODO: check if we want calls by gym_id or branch_id
    branch_result = await session.execute(branch_query)
    branch_ids = [row[0] for row in branch_result]
    
    if not branch_ids:
        return {
            "calls": [],
            "pagination": {
                "total": 0,
                "page": page,
                "page_size": page_size,
                "pages": 0
            }
        }
    
    # Get leads for these branches
    lead_query = select(Lead.id).where(Lead.branch_id.in_(branch_ids))
    lead_result = await session.execute(lead_query)
    lead_ids = [row[0] for row in lead_result]
    
    if not lead_ids:
        return {
            "calls": [],
            "pagination": {
                "total": 0,
                "page": page,
                "page_size": page_size,
                "pages": 0
            }
        }
    
    # Build query for calls in date range
    base_query = (
        select(CallLog)
        .where(and_(
            CallLog.lead_id.in_(lead_ids),
            CallLog.start_time >= start_date,
            CallLog.start_time <= end_date
        ))
    )
    
    # order the calls by start_time

    if sort_order.lower() == "asc":
        base_query = base_query.order_by(CallLog.start_time.asc())
    else:
        base_query = base_query.order_by(CallLog.start_time.desc())
    
    # Count total calls
    count_query = select(func.count()).select_from(base_query.subquery())
    total_count = await session.execute(count_query)
    total = total_count.scalar_one()
    
    # Get calls with pagination
    offset = (page - 1) * page_size
    calls_query = (
        base_query
        .offset(offset)
        .limit(page_size)
    )
    calls_result = await session.execute(calls_query)
    calls = calls_result.scalars().all()
    
    # Get full call data
    call_data = []
    for call in calls:
        call_data.append(await get_call_with_related_data(session, call.id))
    
    return {
        "calls": call_data,
        "pagination": {
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": (total + page_size - 1) // page_size
        }
    }

async def get_calls_by_status_db(
    session: AsyncSession,
    gym_id: str,
    call_status: str,
    start_time: datetime,
    end_time: datetime,
    page: int = 1,
    page_size: int = 50
) -> Dict[str, Any]:
    """
    Get scheduled calls for a time period.
    
    Args:
        session: Database session
        gym_id: Gym ID (branch_id)
        call_status: Call status to filter by
        start_time: Start of the time period
        end_time: End of the time period
        page: Page number
        page_size: Page size
        
    Returns:
        List of scheduled call data
    """
    # First, get branch IDs for the gym
    branch_query = select(Branch.gym_id).where(Branch.gym_id == gym_id)#TODO: check if we want calls by gym_id or branch_id
    branch_result = await session.execute(branch_query)
    branch_ids = [row[0] for row in branch_result]
    
    if not branch_ids:
        return {
            "calls": [],
            "pagination": {
                "total": 0,
                "page": page,
                "page_size": page_size,
                "pages": 0
            }
        }
    
    # Get leads for these branches
    lead_query = select(Lead.id).where(Lead.branch_id.in_(branch_ids))
    lead_result = await session.execute(lead_query)
    lead_ids = [row[0] for row in lead_result]
    
    if not lead_ids:
        return {
            "calls": [],
            "pagination": {
                "total": 0,
                "page": page,
                "page_size": page_size,
                "pages": 0
            }
        }
    
    # Get scheduled calls
    base_query = (
        select(CallLog)
        .where(and_(
            CallLog.lead_id.in_(lead_ids),
            CallLog.call_status == call_status,
            CallLog.start_time >= start_time,
            CallLog.start_time <= end_time
        ))
    )

     # Count total calls
    count_query = select(func.count()).select_from(base_query.subquery())
    total_count = await session.execute(count_query)
    total = total_count.scalar_one()
    
    # Get calls with pagination
    offset = (page - 1) * page_size
    calls_query = (
        base_query
        .offset(offset)
        .limit(page_size)
    )
    scheduled_calls_result = await session.execute(calls_query)
    scheduled_calls = scheduled_calls_result.scalars().all()
    
    # Get full call data
    call_data = []
    for call in scheduled_calls:
        call_data.append(await get_call_with_related_data(session, call.id))
    
    return {
        "calls": call_data,
        "pagination": {
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": (total + page_size - 1) // page_size
        }
    }

async def get_calls_by_outcome_db(
    session: AsyncSession,
    gym_id: str,
    outcome: str,
    page: int = 1,
    page_size: int = 50
) -> Dict[str, Any]:
    """
    Get calls by outcome with pagination.
    
    Args:
        session: Database session
        gym_id: Gym ID (branch_id)
        outcome: Outcome to filter by
        page: Page number
        page_size: Page size
        
    Returns:
        Dictionary containing calls and pagination info
    """
    # First, get branch IDs for the gym
    branch_query = select(Branch.gym_id).where(Branch.gym_id == gym_id) #TODO: check if we want calls by gym_id or branch_id
    branch_result = await session.execute(branch_query)
    branch_ids = [row[0] for row in branch_result]
    
    if not branch_ids:
        return {
            "calls": [],
            "pagination": {
                "total": 0,
                "page": page,
                "page_size": page_size,
                "pages": 0
            }
        }
    
    # Get leads for these branches
    lead_query = select(Lead.id).where(Lead.branch_id.in_(branch_ids))
    lead_result = await session.execute(lead_query)
    lead_ids = [row[0] for row in lead_result]
    
    if not lead_ids:
        return {
            "calls": [],
            "pagination": {
                "total": 0,
                "page": page,
                "page_size": page_size,
                "pages": 0
            }
        }
    
    # Build query for calls with specific outcome
    base_query = (
        select(CallLog)
        .where(and_(
            CallLog.lead_id.in_(lead_ids),
            CallLog.outcome == outcome
        ))
    )
    
    # Count total calls
    count_query = select(func.count()).select_from(base_query.subquery())
    total_count = await session.execute(count_query)
    total = total_count.scalar_one()
    
    # Get calls with pagination
    offset = (page - 1) * page_size
    calls_query = (
        base_query
        .order_by(desc(CallLog.start_time))
        .offset(offset)
        .limit(page_size)
    )
    calls_result = await session.execute(calls_query)
    calls = calls_result.scalars().all()
    
    # Get full call data
    call_data = []
    for call in calls:
        call_data.append(await get_call_with_related_data(session, call.id))
    
    return {
        "calls": call_data,
        "pagination": {
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": (total + page_size - 1) // page_size
        }
    }

#Vishwas.
async def update_call_metrics_db(
    session: AsyncSession,
    call_id: str,
    metrics_data: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    Update call metrics.
    
    Args:
        session: Database session
        call_id: Call ID
        metrics_data: Dictionary containing metric updates
        
    Returns:
        Updated call data if successful, None if call not found
    """
    # Check if call exists
    call_query = select(CallLog).where(CallLog.id == call_id)
    call_result = await session.execute(call_query)
    call = call_result.scalar_one_or_none()
    
    if not call:
        return None
    
    # Update metrics directly in CallLog
    # Extract relevant metrics from metrics_data
    update_data = {}
    if "sentiment" in metrics_data:
        update_data["sentiment"] = metrics_data["sentiment"]
    if "summary" in metrics_data:
        update_data["summary"] = metrics_data["summary"]
    if "duration" in metrics_data:
        update_data["duration"] = metrics_data["duration"]
    if "call_status" in metrics_data:
        update_data["call_status"] = metrics_data["call_status"]
    if "outcome" in metrics_data:
        update_data["outcome"] = metrics_data["outcome"]
    if "transcript" in metrics_data:
        update_data["transcript"] = metrics_data["transcript"]
    if "recording_url" in metrics_data:
        update_data["recording_url"] = metrics_data["recording_url"]
    
    update_query = (
        update(CallLog)
        .where(CallLog.id == call_id)
        .values(**update_data)
    )
    await session.execute(update_query)
    await session.commit()
    
    # Get updated call data
    return await get_call_with_related_data(session, call_id)

async def create_call_log_db(
    session: AsyncSession,
    call_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Create a new call log record.
    
    Args:
        session: Database session
        call_data: Dictionary containing call details
        
    Returns:
        Created call data
    """
    logger.info("Creating new call log record")
    
    call = CallLog(**call_data)
    session.add(call)
    await session.commit()
    await session.refresh(call)
    
    return await get_call_with_related_data(session, call.id)

async def update_call_log_db(
    session: AsyncSession,
    call_id: str,
    call_data: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    Update call log record.
    
    Args:
        session: Database session
        call_id: Call ID
        call_data: Dictionary containing updated call details
        
    Returns:
        Updated call data if successful, None if call not found
    """
    logger.info(f"Updating call log with ID: {call_id}")
    
    query = (
        update(CallLog)
        .where(CallLog.id == call_id)
        .values(**call_data)
    )
    result = await session.execute(query)
    await session.commit()
    
    if result.rowcount == 0:
        return None
    
    return await get_call_with_related_data(session, call_id)

async def delete_call_log_db(
    session: AsyncSession,
    call_id: str
) -> bool:
    """
    Delete a call log record.
    
    Args:
        session: Database session
        call_id: Call ID
        
    Returns:
        True if deleted successfully, False if not found
    """
    logger.info(f"Deleting call log with ID: {call_id}")
    
    # Add cascade delete for related records
    query = (
        delete(CallLog)
        .where(CallLog.id == call_id)
        .execution_options(synchronize_session="fetch")
    )
    result = await session.execute(query)
    await session.commit()
    
    return result.rowcount > 0


# Follow-up call specific functions -> Will be done later.
async def get_follow_up_call_db(
    session: AsyncSession,
    follow_up_call_id: str
) -> Optional[Dict[str, Any]]:
    """
    Get follow-up call details.
    
    Args:
        session: Database session
        follow_up_call_id: Follow-up call ID
        
    Returns:
        Follow-up call data if found, None otherwise
    """
    query = select(FollowUpCall).where(FollowUpCall.id == follow_up_call_id)
    result = await session.execute(query)
    call = result.scalar_one_or_none()
    
    return call.to_dict() if call else None

async def create_follow_up_call_db(
    session: AsyncSession,
    follow_up_call_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Create a new follow-up call record.
    
    Args:
        session: Database session
        follow_up_call_data: Dictionary containing follow-up call details
        
    Returns:
        Created follow-up call data
    """
    logger.info("Creating new follow-up call record")
    
    follow_up_call = FollowUpCall(**follow_up_call_data)
    session.add(follow_up_call)
    await session.commit()
    await session.refresh(follow_up_call)
    
    return follow_up_call.to_dict()

async def update_follow_up_call_db(
    session: AsyncSession,
    follow_up_call_id: str,
    follow_up_call_data: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    Update follow-up call record.
    
    Args:
        session: Database session
        follow_up_call_id: Follow-up call ID
        follow_up_call_data: Dictionary containing updated follow-up call details
        
    Returns:
        Updated follow-up call data if successful, None if not found
    """
    logger.info(f"Updating follow-up call with ID: {follow_up_call_id}")
    
    query = (
        update(FollowUpCall)
        .where(FollowUpCall.id == follow_up_call_id)
        .values(**follow_up_call_data)
    )
    result = await session.execute(query)
    await session.commit()
    
    if result.rowcount == 0:
        return None
    
    return await get_follow_up_call_db(session, follow_up_call_id)

async def delete_follow_up_call_db(
    session: AsyncSession,
    follow_up_call_id: str
) -> bool:
    """
    Delete a follow-up call record.
    
    Args:
        session: Database session
        follow_up_call_id: Follow-up call ID
        
    Returns:
        True if deleted successfully, False if not found
    """
    logger.info(f"Deleting follow-up call with ID: {follow_up_call_id}")
    
    query = delete(FollowUpCall).where(FollowUpCall.id == follow_up_call_id)
    result = await session.execute(query)
    await session.commit()
    
    return result.rowcount > 0

async def get_follow_up_calls_by_campaign_db(
    session: AsyncSession,
    campaign_id: str,
    page: int = 1,
    page_size: int = 50
) -> Dict[str, Any]:
    """
    Get follow-up calls for a campaign with pagination.
    
    Args:
        session: Database session
        campaign_id: Campaign ID
        page: Page number
        page_size: Page size
        
    Returns:
        Dictionary containing follow-up calls and pagination info
    """
    base_query = (
        select(FollowUpCall)
        .outerjoin(FollowUpCall.campaign)
        .where(FollowUpCall.campaign_id == campaign_id)
    )
    
    # Get total count using subquery for 1.4 compatibility
    count_query = select(func.count(1)).select_from(base_query.subquery())
    total_result = await session.execute(count_query)
    total_calls = total_result.scalar_one()
    
    # Get paginated results
    offset = (page - 1) * page_size
    query = base_query.order_by(desc(FollowUpCall.call_date_time)).offset(offset).limit(page_size)
    result = await session.execute(query)
    calls = result.unique().scalars().all()
    
    # Convert to dictionaries
    calls_data = [call.to_dict() for call in calls]
    
    return {
        "follow_up_calls": calls_data,
        "pagination": {
            "total": total_calls,
            "page": page,
            "page_size": page_size,
            "pages": (total_calls + page_size - 1) // page_size
        }
    }

async def get_follow_up_calls_by_lead_db(
    session: AsyncSession,
    lead_id: str,
    page: int = 1,
    page_size: int = 50
) -> Dict[str, Any]:
    """
    Get follow-up calls for a lead with pagination.
    
    Args:
        session: Database session
        lead_id: Lead ID
        page: Page number
        page_size: Page size
        
    Returns:
        Dictionary containing follow-up calls and pagination info
    """
    base_query = select(FollowUpCall).where(FollowUpCall.lead_id == lead_id)
    
    # Get total count
    count_query = select(func.count()).select_from(base_query.subquery())
    total = await session.execute(count_query)
    total_calls = total.scalar_one()
    
    # Get paginated results
    offset = (page - 1) * page_size
    query = base_query.order_by(desc(FollowUpCall.call_date_time)).offset(offset).limit(page_size)
    result = await session.execute(query)
    calls = result.scalars().all()
    
    # Convert to dictionaries
    calls_data = [call.to_dict() for call in calls]
    
    return {
        "follow_up_calls": calls_data,
        "pagination": {
            "total": total_calls,
            "page": page,
            "page_size": page_size,
            "pages": (total_calls + page_size - 1) // page_size
        }
    }