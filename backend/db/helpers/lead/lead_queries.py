"""
Database helper functions for lead-related operations.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy import select, and_, or_, func, desc, update, insert, delete, join
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from ...models.lead import Lead
from ...models.lead.lead_tag import lead_tag
from ...models.lead.tag import Tag
from ...models.call.call_log import CallLog
from ...models.campaign.follow_up_campaign import FollowUpCampaign
from ...models.member import Member
from ...models.call.follow_up_call import FollowUpCall
from ...models.gym.branch import Branch
from ....utils.logging.logger import get_logger

logger = get_logger(__name__)

#Tested Works
async def get_lead_with_related_data(session: AsyncSession, lead_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a lead with all related data.
    
    Args:
        session: Database session
        lead_id: Lead ID
        
    Returns:
        Lead data with related information or None if not found
    """
    # Get lead with unique() for 1.4 compatibility
    lead_query = select(Lead).where(Lead.id == lead_id)
    lead_result = await session.execute(lead_query)
    lead = lead_result.unique().scalar_one_or_none()
    
    if not lead:
        return None
    
    lead_dict = lead.to_dict()
    
    # Get tags
    tags_query = (
        select(Tag)
        .join(lead_tag, Tag.id == lead_tag.c.tag_id)
        .where(lead_tag.c.lead_id == lead_id)
    )
    tags_result = await session.execute(tags_query)
    tags = tags_result.scalars().all()
    lead_dict["tags"] = [tag.to_dict() for tag in tags]
    
    # Get qualification from lead directly
    lead_dict["qualification"] = lead.qualification_score
    lead_dict["qualification_notes"] = lead.qualification_notes
    
    # Get last call
    call_query = (
        select(CallLog)
        .where(CallLog.lead_id == lead_id)
        .order_by(desc(CallLog.created_at))
        .limit(1)
    )
    call_result = await session.execute(call_query)
    last_call = call_result.scalar_one_or_none()
    lead_dict["last_call"] = last_call.to_dict() if last_call else None
    
    return lead_dict

#Tested Works
async def create_lead_db(
    session: AsyncSession,
    lead_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Create a new lead.
    
    Args:
        session: Database session
        lead_data: Dictionary containing lead details
        
    Returns:
        Created lead data
    """
    logger.info("Creating new lead record")
    
    lead = Lead(**lead_data)
    session.add(lead)
    await session.commit()
    await session.refresh(lead)
    
    return await get_lead_with_related_data(session, lead.id)

#Tested Works
async def update_lead_db(
    session: AsyncSession,
    lead_id: str,
    lead_data: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    Update lead record.
    
    Args:
        session: Database session
        lead_id: Lead ID
        lead_data: Dictionary containing updated lead details
        
    Returns:
        Updated lead data if successful, None if not found
    """
    logger.info(f"Updating lead with ID: {lead_id}")
    
    query = (
        update(Lead)
        .where(Lead.id == lead_id)
        .values(**lead_data)
    )
    result = await session.execute(query)
    await session.commit()
    
    if result.rowcount == 0:
        return None
    
    return await get_lead_with_related_data(session, lead_id)

#Tested Works
async def delete_lead_db(
    session: AsyncSession,
    lead_id: str
) -> bool:
    """
    Delete a lead record with cascade.
    
    Args:
        session: Database session
        lead_id: Lead ID
        
    Returns:
        True if deleted successfully, False if not found
    """
    logger.info(f"Deleting lead with ID: {lead_id}")
    
    try:
        # First delete related records
        # Delete call logs
        await session.execute(
            delete(CallLog)
            .where(CallLog.lead_id == lead_id)
            .execution_options(synchronize_session="fetch")
        )
        
        # Delete follow-up calls
        await session.execute(
            delete(FollowUpCall)
            .where(FollowUpCall.lead_id == lead_id)
            .execution_options(synchronize_session="fetch")
        )
        
        # Delete tags associations
        await session.execute(
            delete(lead_tag)
            .where(lead_tag.c.lead_id == lead_id)
            .execution_options(synchronize_session="fetch")
        )
        
        # Delete follow-up campaigns
        await session.execute(
            delete(FollowUpCampaign)
            .where(FollowUpCampaign.lead_id == lead_id)
            .execution_options(synchronize_session="fetch")
        )
        
        # Finally delete the lead
        query = (
            delete(Lead)
            .where(Lead.id == lead_id)
            .execution_options(synchronize_session="fetch")
        )
        result = await session.execute(query)
        await session.commit()
        
        return result.rowcount > 0
        
    except Exception as e:
        await session.rollback()
        logger.error(f"Error deleting lead {lead_id}: {str(e)}")
        raise

async def get_converted_leads_db(
    session: AsyncSession,
    gym_id: str,
    page: int = 1,
    page_size: int = 50
) -> Dict[str, Any]:
    """
    Get leads that have been converted to members with pagination.
    
    Args:
        session: Database session
        gym_id: Gym ID
        page: Page number
        page_size: Page size
        
    Returns:
        Dictionary containing converted leads and pagination info
    """
    # Query leads that have associated members
    base_query = (
        select(Lead)
        .join(Member, Lead.id == Member.lead_id)
        .outerjoin(Lead.tags)  # Explicit joins for relationships
        .where(Lead.gym_id == gym_id)
        .group_by(Lead.id)
    )
    
    # Get total count
    count_query = select(func.count()).select_from(base_query.subquery())
    total = await session.execute(count_query)
    total_converted = total.scalar_one()
    
    # Get paginated results
    offset = (page - 1) * page_size
    query = base_query.order_by(desc(Lead.updated_at)).offset(offset).limit(page_size)
    result = await session.execute(query)
    leads = result.scalars().all()
    
    # Get full lead data with member information
    converted_data = []
    for lead in leads:
        lead_data = await get_lead_with_related_data(session, lead.id)
        # Add member information
        member_query = select(Member).where(Member.lead_id == lead.id)
        member_result = await session.execute(member_query)
        member = member_result.scalar_one_or_none()
        if member:
            lead_data["member"] = member.to_dict()
        converted_data.append(lead_data)
    
    return {
        "converted_leads": converted_data,
        "pagination": {
            "total": total_converted,
            "page": page,
            "page_size": page_size,
            "pages": (total_converted + page_size - 1) // page_size
        }
    }

async def get_lead_conversion_details_db(
    session: AsyncSession,
    lead_id: str
) -> Optional[Dict[str, Any]]:
    """
    Get conversion details for a lead.
    
    Args:
        session: Database session
        lead_id: Lead ID
        
    Returns:
        Dictionary containing lead and member details if converted,
        lead details only if not converted, None if lead not found
    """
    # Get lead data
    lead_data = await get_lead_with_related_data(session, lead_id)
    if not lead_data:
        return None
    
    # Check for member conversion
    member_query = select(Member).where(Member.lead_id == lead_id)
    member_result = await session.execute(member_query)
    member = member_result.scalar_one_or_none()
    
    if member:
        lead_data["converted"] = True
        lead_data["member"] = member.to_dict()
    else:
        lead_data["converted"] = False
    
    return lead_data

async def get_leads_by_assigned_user_db(
    session: AsyncSession,
    user_id: str,
    page: int = 1,
    page_size: int = 50
) -> Dict[str, Any]:
    """
    Get all leads assigned to a specific user with pagination.
    
    Args:
        session: Database session
        user_id: User ID
        page: Page number
        page_size: Page size
        
    Returns:
        Dictionary containing assigned leads and pagination info
    """
    base_query = select(Lead).where(Lead.assigned_to_user_id == user_id)
    
    # Get total count
    count_query = select(func.count()).select_from(base_query.subquery())
    total = await session.execute(count_query)
    total_leads = total.scalar_one()
    
    # Get paginated results
    offset = (page - 1) * page_size
    query = base_query.order_by(desc(Lead.updated_at)).offset(offset).limit(page_size)
    result = await session.execute(query)
    leads = result.scalars().all()
    
    # Get full lead data
    leads_data = []
    for lead in leads:
        leads_data.append(await get_lead_with_related_data(session, lead.id))
    
    return {
        "leads": leads_data,
        "pagination": {
            "total": total_leads,
            "page": page,
            "page_size": page_size,
            "pages": (total_leads + page_size - 1) // page_size
        }
    }

def build_lead_filters(base_query, filters: Dict[str, Any]):
    """
    Build query filters for lead queries.
    
    Args:
        base_query: Base SQLAlchemy query
        filters: Dictionary of filters
        
    Returns:
        Query with filters applied
    """
    conditions = []
    
    # Status filter - check for both "status" and "lead_status" keys
    if "status" in filters:
        status = filters["status"]
        if isinstance(status, list):
            conditions.append(Lead.lead_status.in_(status))
        else:
            conditions.append(Lead.lead_status == status)
    elif "lead_status" in filters:
        status = filters["lead_status"]
        if isinstance(status, list):
            conditions.append(Lead.lead_status.in_(status))
        else:
            conditions.append(Lead.lead_status == status)
    
    # Search filter (name, email, phone)
    if "search" in filters and filters["search"]:
        search_term = f"%{filters['search']}%"
        conditions.append(or_(
            Lead.first_name.ilike(search_term),
            Lead.last_name.ilike(search_term),
            Lead.email.ilike(search_term),
            Lead.phone.ilike(search_term)
        ))
    
    # Date range filter
    if "date_from" in filters:
        conditions.append(Lead.created_at >= filters["date_from"])
    
    if "date_to" in filters:
        conditions.append(Lead.created_at <= filters["date_to"])
    
    # Tag filter
    if "tags" in filters and filters["tags"]:
        tags = filters["tags"]
        if isinstance(tags, list):
            # Join with tags table to filter by tag names
            tag_subquery = (
                select(lead_tag.c.lead_id)
                .join(Tag, Tag.id == lead_tag.c.tag_id)
                .where(Tag.name.in_(tags))
                .group_by(lead_tag.c.lead_id)
                .having(func.count(lead_tag.c.tag_id) == len(tags))
            )
        else:
            # Single tag filter
            tag_subquery = (
                select(lead_tag.c.lead_id)
                .join(Tag, Tag.id == lead_tag.c.tag_id)
                .where(Tag.name == tags)
            )
        
        conditions.append(Lead.id.in_(tag_subquery))
    
    # Qualification filter
    if "qualification" in filters:
        qualification = filters["qualification"]
        # Use the qualification_score field directly
        conditions.append(Lead.qualification_score == qualification)
    
    # Campaign filter
    if "campaign_id" in filters:
        # Use the relationship between leads and campaigns
        campaign_subquery = (
            select(FollowUpCampaign.lead_id)
            .where(FollowUpCampaign.id == filters["campaign_id"])
        )
        conditions.append(Lead.id.in_(campaign_subquery))
    
    if conditions:
        return base_query.where(and_(*conditions))
    
    return base_query

#Tested Works
async def get_leads_by_gym_with_filters(
    session: AsyncSession,
    branch_id: str,
    filters: Optional[Dict[str, Any]] = None,
    page: int = 1,
    page_size: int = 50
) -> Dict[str, Any]:
    """
    Get all leads for a gym with optional filters.
    
    Args:
        session: Database session
        branch_id: Gym ID
        filters: Optional filters
        page: Page number
        page_size: Page size
        
    Returns:
        Dictionary containing leads and pagination info
    
    Raises:
        ValueError: If invalid parameters are provided
        Exception: For database or other errors
    """
    try:
        # Validate inputs
        if not branch_id:
            raise ValueError("Branch ID is required")
        
        if page < 1:
            raise ValueError("Page number must be at least 1")
        
        if page_size < 1:
            raise ValueError("Page size must be at least 1")
        
        # Start with base query
        base_query = (
            select(Lead)
            .outerjoin(Lead.tags)  # Explicit join for relationships
            .outerjoin(Lead.call_logs)
            .outerjoin(Lead.appointments)
            .where(Lead.branch_id == branch_id)
            .group_by(Lead.id)
        )
        
        # Apply filters
        if filters:
            try:
                base_query = build_lead_filters(base_query, filters)
            except Exception as e:
                raise ValueError(f"Invalid filter parameters: {str(e)}")
        
        # Count total
        count_query = select(func.count()).select_from(base_query.subquery())
        total_count = await session.execute(count_query)
        total = total_count.scalar_one()
        
        # Apply pagination
        offset = (page - 1) * page_size
        query = base_query.order_by(desc(Lead.created_at)).offset(offset).limit(page_size)
        
        # Execute query
        result = await session.execute(query)
        leads = result.scalars().all()
        
        # Get full lead data
        lead_data = []
        for lead in leads:
            lead_data.append(await get_lead_with_related_data(session, lead.id))
        
        return {
            "leads": lead_data,
            "pagination": {
                "total": total,
                "page": page,
                "page_size": page_size,
                "pages": (total + page_size - 1) // page_size
            }
        }
    except ValueError as ve:
        # Re-raise validation errors
        raise
    except Exception as e:
        # Log and re-raise other errors
        logger.error(f"Error fetching leads for branch {branch_id}: {str(e)}")
        raise Exception(f"Failed to retrieve leads: {str(e)}")

async def update_lead_after_call_db(
    session: AsyncSession,
    lead_id: str,
    call_data: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    Update lead information after a call in the database.
    
    Args:
        session: Database session
        lead_id: Lead ID
        call_data: Call data containing outcome and summary
        
    Returns:
        Updated lead data if successful, None if lead not found
    """
    logger.info(f"Updating lead {lead_id} after call with outcome: {call_data.get('outcome')}")
    
    # Check if lead exists
    lead_query = select(Lead).where(Lead.id == lead_id)
    lead_result = await session.execute(lead_query)
    lead = lead_result.scalar_one_or_none()
    
    if not lead:
        logger.error(f"Lead with ID {lead_id} not found")
        return None
    
    # Update lead based on call data
    updates = {
        "last_called": datetime.now(),
        "last_conversation_summary": call_data.get("notes", "")
    }
    
    # Update status based on outcome
    outcome = call_data.get("outcome")
    if outcome:
        logger.info(f"Processing outcome: {outcome}")
        if outcome == "scheduled":
            updates["lead_status"] = "scheduled"
        elif outcome == "not_interested":
            updates["lead_status"] = "closed"
        elif outcome == "interested":
            updates["lead_status"] = "qualified"
        elif outcome == "callback":
            updates["lead_status"] = "callback"
        else:
            # For unknown outcomes, default to contacted
            updates["lead_status"] = "contacted"
            logger.warning(f"Unknown outcome type: {outcome}, defaulting to 'contacted'")
    
    # Update lead record
    update_query = (
        update(Lead)
        .where(Lead.id == lead_id)
        .values(**updates)
    )
    await session.execute(update_query)
    await session.commit()
    
    logger.info(f"Updated lead {lead_id} status to {updates.get('lead_status')}")
    
    # Get updated lead data
    return await get_lead_with_related_data(session, lead_id)

#No errors
async def get_prioritized_leads_db(
    session: AsyncSession,
    branch_id: str,
    count: int,
    qualification: Optional[str] = None,
    exclude_leads: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    Get prioritized leads for campaigns from the database.
    
    Args:
        session: Database session
        branch_id: Gym ID (branch_id in the Lead model)
        count: Number of leads to return
        qualification: Optional qualification filter
        exclude_leads: Optional list of lead IDs to exclude
        
    Returns:
        List of prioritized lead data
    """
    # Start with base query
    base_query = select(Lead).where(Lead.branch_id == branch_id)
    
    # Apply qualification filter if provided
    if qualification:
        base_query = base_query.where(Lead.qualification_score == qualification)
    
    # Exclude leads if provided
    if exclude_leads:
        base_query = base_query.where(Lead.id.not_in(exclude_leads))
    
    # Prioritize leads:
    # 1. Leads with no calls
    # 2. Leads with oldest last call
    # 3. Leads with callback status
    
    # Get leads with no calls
    no_calls_subquery = (
        select(Lead.id)
        .outerjoin(CallLog, Lead.id == CallLog.lead_id)
        .where(CallLog.id == None)
        .where(Lead.branch_id == branch_id)
    )
    
    if qualification:
        no_calls_subquery = no_calls_subquery.where(Lead.qualification_score == qualification)
    
    if exclude_leads:
        no_calls_subquery = no_calls_subquery.where(Lead.id.not_in(exclude_leads))
    
    no_calls_query = select(Lead).where(Lead.id.in_(no_calls_subquery)).limit(count)
    no_calls_result = await session.execute(no_calls_query)
    no_calls_leads = no_calls_result.scalars().all()
    
    # If we have enough leads with no calls, return them
    if len(no_calls_leads) >= count:
        return [await get_lead_with_related_data(session, lead.id) for lead in no_calls_leads[:count]]
    
    # Get leads with oldest last call
    remaining_count = count - len(no_calls_leads)
    
    # Subquery to get the last call time for each lead
    last_call_subquery = (
        select(
            CallLog.lead_id,
            func.max(CallLog.created_at).label("last_call_time")
        )
        .group_by(CallLog.lead_id)
        .subquery()
    )
    
    oldest_calls_query = (
        select(Lead)
        .join(last_call_subquery, Lead.id == last_call_subquery.c.lead_id)
        .where(Lead.branch_id == branch_id)
    )
    
    if qualification:
        oldest_calls_query = oldest_calls_query.where(Lead.qualification_score == qualification)
    
    if exclude_leads:
        oldest_calls_query = oldest_calls_query.where(Lead.id.not_in(exclude_leads))
    
    # Exclude leads we already have
    no_calls_ids = [lead.id for lead in no_calls_leads]
    if no_calls_ids:
        oldest_calls_query = oldest_calls_query.where(Lead.id.not_in(no_calls_ids))
    
    oldest_calls_query = oldest_calls_query.order_by(last_call_subquery.c.last_call_time).limit(remaining_count)
    oldest_calls_result = await session.execute(oldest_calls_query)
    oldest_calls_leads = oldest_calls_result.scalars().all()
    
    # Combine results
    all_leads = list(no_calls_leads) + list(oldest_calls_leads)
    
    return [await get_lead_with_related_data(session, lead.id) for lead in all_leads]

async def get_leads_for_retry_db(
    session: AsyncSession,
    campaign_id: str,
    gap_days: int
) -> List[Dict[str, Any]]:
    """
    Get leads eligible for retry calls from the database.
    
    Args:
        session: Database session
        campaign_id: Campaign ID
        gap_days: Minimum days since last call
        
    Returns:
        List of lead data eligible for retry
    """
    # Get campaign leads
    campaign_leads_query = select(FollowUpCampaign.lead_id).where(FollowUpCampaign.id == campaign_id)
    campaign_leads_result = await session.execute(campaign_leads_query)
    campaign_lead_ids = [row[0] for row in campaign_leads_result]
    
    if not campaign_lead_ids:
        return []
    
    # Calculate cutoff date
    cutoff_date = datetime.now() - timedelta(days=gap_days)
    
    # Subquery to get the last call time for each lead
    last_call_subquery = (
        select(
            CallLog.lead_id,
            func.max(CallLog.created_at).label("last_call_time")
        )
        .where(CallLog.lead_id.in_(campaign_lead_ids))
        .group_by(CallLog.lead_id)
        .subquery()
    )
    
    # Get leads with last call before cutoff date
    retry_query = (
        select(Lead)
        .join(last_call_subquery, Lead.id == last_call_subquery.c.lead_id)
        .where(last_call_subquery.c.last_call_time < cutoff_date)
    )
    
    retry_result = await session.execute(retry_query)
    retry_leads = retry_result.scalars().all()
    
    return [await get_lead_with_related_data(session, lead.id) for lead in retry_leads]