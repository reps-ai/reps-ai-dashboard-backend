"""
Database helper functions for campaign-related operations.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy import select, and_, or_, func, desc, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.campaign.follow_up_campaign import FollowUpCampaign
from ...models.call.follow_up_call import FollowUpCall
from ...models.lead import Lead
from ...models.gym.branch import Branch
from ...models.gym.gym import Gym
from ....utils.logging.logger import get_logger

logger = get_logger(__name__)

async def get_campaign_with_related_data(session: AsyncSession, campaign_id: str) -> Optional[Dict[str, Any]]:
    """
    Get campaign with related data using the provided session.
    
    Args:
        session: Database session to use - MUST be the shared session
        campaign_id: ID of the campaign
        
    Returns:
        Dictionary containing campaign details and related data
    """
    # Important: Use the provided session, don't create a new one
    query = select(FollowUpCampaign).where(FollowUpCampaign.id == campaign_id)
    result = await session.execute(query)
    campaign = result.unique().scalar_one_or_none()
    
    if not campaign:
        return None
        
    campaign_dict = campaign.to_dict()
    
    # Get lead information
    lead_query = select(Lead).where(Lead.id == campaign.lead_id)
    lead_result = await session.execute(lead_query)
    lead = lead_result.scalar_one_or_none()
    if lead:
        campaign_dict["lead"] = {
            "id": lead.id,
            "first_name": lead.first_name,
            "last_name": lead.last_name,
            "phone": lead.phone,
            "email": lead.email
        }
    
    # Get branch and gym information
    branch_query = select(Branch).where(Branch.id == campaign.branch_id)
    branch_result = await session.execute(branch_query)
    branch = branch_result.scalar_one_or_none()
    if branch:
        campaign_dict["branch"] = {
            "id": branch.id,
            "name": branch.name
        }
    
    gym_query = select(Gym).where(Gym.id == campaign.gym_id)
    gym_result = await session.execute(gym_query)
    gym = gym_result.scalar_one_or_none()
    if gym:
        campaign_dict["gym"] = {
            "id": gym.id,
            "name": gym.name
        }
    
    # Get call stats
    calls_query = select(func.count(FollowUpCall.id)).where(FollowUpCall.campaign_id == campaign_id)
    total_calls = await session.execute(calls_query)
    campaign_dict["total_calls"] = total_calls.scalar_one()
    
    return campaign_dict

async def create_campaign_db(
    session: AsyncSession,
    campaign_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Create a new campaign.
    
    Args:
        session: Database session
        campaign_data: Dictionary containing campaign data
        
    Returns:
        Created campaign data
    """
    campaign = FollowUpCampaign(**campaign_data)
    session.add(campaign)
    await session.commit()
    await session.refresh(campaign)
    
    return await get_campaign_with_related_data(session, campaign.id)

async def update_campaign_db(
    session: AsyncSession,
    campaign_id: str,
    campaign_data: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    Update a campaign.
    
    Args:
        session: Database session
        campaign_id: Campaign ID
        campaign_data: Dictionary containing campaign updates
        
    Returns:
        Updated campaign data if successful, None if campaign not found
    """
    query = (
        update(FollowUpCampaign)
        .where(FollowUpCampaign.id == campaign_id)
        .values(**campaign_data)
    )
    result = await session.execute(query)
    await session.commit()
    
    if result.rowcount == 0:
        return None
        
    return await get_campaign_with_related_data(session, campaign_id)

async def delete_campaign_db(
    session: AsyncSession,
    campaign_id: str
) -> bool:
    """
    Delete a campaign with cascade delete for related records.
    
    Args:
        session: Database session
        campaign_id: Campaign ID
        
    Returns:
        True if campaign was deleted, False if not found
    """
    logger.info(f"Deleting campaign with ID: {campaign_id}")
    
    try:
        # First delete related follow-up calls
        follow_up_calls_query = delete(FollowUpCall).where(
            FollowUpCall.campaign_id == campaign_id
        ).execution_options(synchronize_session="fetch")
        await session.execute(follow_up_calls_query)
        
        # Delete the campaign record
        campaign_query = delete(FollowUpCampaign).where(
            FollowUpCampaign.id == campaign_id
        ).execution_options(synchronize_session="fetch")
        result = await session.execute(campaign_query)
        await session.commit()
        
        return result.rowcount > 0
        
    except Exception as e:
        await session.rollback()
        logger.error(f"Error deleting campaign {campaign_id}: {str(e)}")
        raise

async def get_campaigns_by_lead_db(
    session: AsyncSession,
    lead_id: str,
    page: int = 1,
    page_size: int = 50
) -> Dict[str, Any]:
    """
    Get all campaigns for a lead with pagination.
    
    Args:
        session: Database session
        lead_id: Lead ID
        page: Page number
        page_size: Page size
        
    Returns:
        Dictionary containing campaigns and pagination info
    """
    base_query = (
        select(FollowUpCampaign)
        .outerjoin(FollowUpCampaign.lead)  # Explicit join for 1.4
        .where(FollowUpCampaign.lead_id == lead_id)
    )
    
    # Get total count using subquery for 1.4 compatibility
    count_query = select(func.count(1)).select_from(base_query.subquery())
    total = await session.execute(count_query)
    total_campaigns = total.scalar_one()
    
    # Get paginated results
    offset = (page - 1) * page_size
    query = base_query.order_by(desc(FollowUpCampaign.created_at)).offset(offset).limit(page_size)
    result = await session.execute(query)
    campaigns = result.unique().scalars().all()  # Use unique() for relationships
    
    # Get full campaign data
    campaign_data = []
    for campaign in campaigns:
        campaign_data.append(await get_campaign_with_related_data(session, campaign.id))
    
    return {
        "campaigns": campaign_data,
        "pagination": {
            "total": total_campaigns,
            "page": page,
            "page_size": page_size,
            "pages": (total_campaigns + page_size - 1) // page_size
        }
    }

async def get_campaigns_by_status_db(
    session: AsyncSession,
    gym_id: str,
    status: str,
    page: int = 1,
    page_size: int = 50
) -> Dict[str, Any]:
    """
    Get campaigns by status with pagination.
    
    Args:
        session: Database session
        gym_id: Gym ID
        status: Campaign status to filter by
        page: Page number
        page_size: Page size
        
    Returns:
        Dictionary containing campaigns and pagination info
    """
    base_query = (
        select(FollowUpCampaign)
        .outerjoin(FollowUpCampaign.lead)  # Explicit join for 1.4
        .where(and_(
            FollowUpCampaign.gym_id == gym_id,
            FollowUpCampaign.campaign_status == status
        ))
    )
    
    # Get total count using subquery for 1.4 compatibility
    count_query = select(func.count(1)).select_from(base_query.subquery())
    total = await session.execute(count_query)
    total_campaigns = total.scalar_one()
    
    # Get paginated results with unique() for relationships
    offset = (page - 1) * page_size
    query = base_query.order_by(desc(FollowUpCampaign.created_at)).offset(offset).limit(page_size)
    result = await session.execute(query)
    campaigns = result.unique().scalars().all()
    
    # Get full campaign data
    campaign_data = []
    for campaign in campaigns:
        campaign_data.append(await get_campaign_with_related_data(session, campaign.id))
    
    return {
        "campaigns": campaign_data,
        "pagination": {
            "total": total_campaigns,
            "page": page,
            "page_size": page_size,
            "pages": (total_campaigns + page_size - 1) // page_size
        }
    }

async def update_campaign_status_db(
    session: AsyncSession,
    campaign_id: str,
    new_status: str
) -> Optional[Dict[str, Any]]:
    """
    Update campaign status.
    
    Args:
        session: Database session
        campaign_id: Campaign ID
        new_status: New campaign status
        
    Returns:
        Updated campaign data if successful, None if campaign not found
    """
    query = (
        update(FollowUpCampaign)
        .where(FollowUpCampaign.id == campaign_id)
        .values(campaign_status=new_status)
    )
    result = await session.execute(query)
    await session.commit()
    
    if result.rowcount == 0:
        return None
        
    return await get_campaign_with_related_data(session, campaign_id)