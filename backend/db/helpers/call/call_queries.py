"""
Database helper functions for call-related operations.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy import select, and_, or_, func, desc, update
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from ...models.call.call_log import CallLog
from ...models.lead import Lead
from ...models.campaign.follow_up_campaign import FollowUpCampaign
from ...models.call.follow_up_call import FollowUpCall
from ...models.user import User
from ...models.gym.branch import Branch
from ...models.gym.gym import Gym
from ....utils.logging.logger import get_logger


logger = get_logger(__name__)

async def get_call_with_related_data(call_id: str, session: AsyncSession) -> Optional[Dict[str, Any]]:
    """
    Get a call with all related data.
    
    Args:
        session: Database session
        call_id: Call ID
        
    Returns:
        Call data with related information or None if not found
    """
    # Get call
    call_query = select(CallLog).where(CallLog.id == call_id)
    call_result = await session.execute(call_query)
    call = call_result.scalar_one_or_none()
    
    if not call:
        return None
    
    call_dict = call.to_dict()
    
    # Get lead information
    if call.lead_id:
        lead_query = select(Lead).where(Lead.id == call.lead_id)
        lead_result = await session.execute(lead_query)
        lead = lead_result.scalar_one_or_none()
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
    page_size: int = 50
) -> Dict[str, Any]:
    """
    Get all calls for a campaign with pagination.
    
    Args:
        session: Database session
        campaign_id: Campaign ID
        page: Page number
        page_size: Page size
        
    Returns:
        Dictionary containing calls and pagination info
    """
    # Get calls for the campaign directly from CallLog
    base_query = select(CallLog).where(CallLog.campaign_id == campaign_id)
    
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

async def get_calls_by_lead_db(
    session: AsyncSession,
    lead_id: str,
    page: int = 1,
    page_size: int = 50
) -> Dict[str, Any]:
    """
    Get all calls for a lead with pagination.
    
    Args:
        session: Database session
        lead_id: Lead ID
        page: Page number
        page_size: Page size
        
    Returns:
        Dictionary containing calls and pagination info
    """
    # Get calls for the lead directly from CallLog
    base_query = select(CallLog).where(CallLog.lead_id == lead_id)
    
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

async def get_calls_by_date_range_db(
    session: AsyncSession,
    gym_id: str,
    start_date: datetime,
    end_date: datetime,
    page: int = 1,
    page_size: int = 50
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
        
    Returns:
        Dictionary containing calls and pagination info
    """
    # First, get branch IDs for the gym
    branch_query = select(Branch.id).where(Branch.id == gym_id)
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

async def get_active_calls_db(
    session: AsyncSession,
    gym_id: str
) -> List[Dict[str, Any]]:
    """
    Get all active calls for a gym.
    
    Args:
        session: Database session
        gym_id: Gym ID (branch_id)
        
    Returns:
        List of active call data
    """
    # First, get branch IDs for the gym
    branch_query = select(Branch.id).where(Branch.id == gym_id)
    branch_result = await session.execute(branch_query)
    branch_ids = [row[0] for row in branch_result]
    
    if not branch_ids:
        return []
    
    # Get leads for these branches
    lead_query = select(Lead.id).where(Lead.branch_id.in_(branch_ids))
    lead_result = await session.execute(lead_query)
    lead_ids = [row[0] for row in lead_result]
    
    if not lead_ids:
        return []
    
    # Get active calls (status = 'in_progress')
    active_calls_query = (
        select(CallLog)
        .where(and_(
            CallLog.lead_id.in_(lead_ids),
            CallLog.call_status == 'in_progress'
        ))
    )
    active_calls_result = await session.execute(active_calls_query)
    active_calls = active_calls_result.scalars().all()
    
    # Get full call data
    call_data = []
    for call in active_calls:
        call_data.append(await get_call_with_related_data(session, call.id))
    
    return call_data

async def get_scheduled_calls_db(
    session: AsyncSession,
    gym_id: str,
    start_time: datetime,
    end_time: datetime
) -> List[Dict[str, Any]]:
    """
    Get scheduled calls for a time period.
    
    Args:
        session: Database session
        gym_id: Gym ID (branch_id)
        start_time: Start of the time period
        end_time: End of the time period
        
    Returns:
        List of scheduled call data
    """
    # First, get branch IDs for the gym
    branch_query = select(Branch.id).where(Branch.id == gym_id)
    branch_result = await session.execute(branch_query)
    branch_ids = [row[0] for row in branch_result]
    
    if not branch_ids:
        return []
    
    # Get leads for these branches
    lead_query = select(Lead.id).where(Lead.branch_id.in_(branch_ids))
    lead_result = await session.execute(lead_query)
    lead_ids = [row[0] for row in lead_result]
    
    if not lead_ids:
        return []
    
    # Get scheduled calls
    scheduled_calls_query = (
        select(CallLog)
        .where(and_(
            CallLog.lead_id.in_(lead_ids),
            CallLog.call_status == 'scheduled',
            CallLog.start_time >= start_time,
            CallLog.start_time <= end_time
        ))
        .order_by(CallLog.start_time)
    )
    scheduled_calls_result = await session.execute(scheduled_calls_query)
    scheduled_calls = scheduled_calls_result.scalars().all()
    
    # Get full call data
    call_data = []
    for call in scheduled_calls:
        call_data.append(await get_call_with_related_data(session, call.id))
    
    return call_data

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
    branch_query = select(Branch.id).where(Branch.id == gym_id)
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

async def update_call_recording_db(
    session: AsyncSession,
    call_id: str,
    recording_url: str
) -> Optional[Dict[str, Any]]:
    """
    Update call recording URL.
    
    Args:
        session: Database session
        call_id: Call ID
        recording_url: URL of the recording
        
    Returns:
        Updated call data if successful, None if call not found
    """
    # Check if call exists
    call_query = select(CallLog).where(CallLog.id == call_id)
    call_result = await session.execute(call_query)
    call = call_result.scalar_one_or_none()
    
    if not call:
        return None
    
    # Update recording URL directly in CallLog
    update_query = (
        update(CallLog)
        .where(CallLog.id == call_id)
        .values(recording_url=recording_url)
    )
    await session.execute(update_query)
    await session.commit()
    
    # Get updated call data
    return await get_call_with_related_data(session, call_id)

async def update_call_transcript_db(
    session: AsyncSession,
    call_id: str,
    transcript: str
) -> Optional[Dict[str, Any]]:
    """
    Update call transcript.
    
    Args:
        session: Database session
        call_id: Call ID
        transcript: Call transcript text
        
    Returns:
        Updated call data if successful, None if call not found
    """
    # Check if call exists
    call_query = select(CallLog).where(CallLog.id == call_id)
    call_result = await session.execute(call_query)
    call = call_result.scalar_one_or_none()
    
    if not call:
        return None
    
    # Update transcript directly in CallLog
    update_query = (
        update(CallLog)
        .where(CallLog.id == call_id)
        .values(transcript=transcript)
    )
    await session.execute(update_query)
    await session.commit()
    
    # Get updated call data
    return await get_call_with_related_data(session, call_id)

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
    
    update_query = (
        update(CallLog)
        .where(CallLog.id == call_id)
        .values(**update_data)
    )
    await session.execute(update_query)
    await session.commit()
    
    # Get updated call data
    return await get_call_with_related_data(session, call_id) 