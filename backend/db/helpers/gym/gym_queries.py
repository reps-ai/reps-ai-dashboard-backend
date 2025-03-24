"""
Database helper functions for gym-related operations.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy import select, and_, or_, func, desc, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.gym.gym import Gym
from ...models.gym.branch import Branch
from ...models.member import Member
from ...models.user import User, user_branch  # Added user_branch import
from ...models.gym.gym_settings import GymSettings
from ...models.call.call_settings import CallSettings
from ...models.ai_settings import AISettings
from ...models.voice_settings import VoiceSettings
from ....utils.logging.logger import get_logger

logger = get_logger(__name__)

async def get_gym_with_related_data(session: AsyncSession, gym_id: str) -> Optional[Dict[str, Any]]:
    """Get a gym with all related data."""
    # Use unique() for 1.4 compatibility with relationships
    query = select(Gym).where(Gym.id == gym_id)
    result = await session.execute(query)
    gym = result.unique().scalar_one_or_none()
    
    if not gym:
        return None
        
    # Get branches count
    branches_count = await session.execute(
        select(func.count(Branch.id)).where(Branch.gym_id == gym_id)
    )
    # Get members count
    members_count = await session.execute(
        select(func.count(Member.id)).where(Member.gym_id == gym_id)
    )
    # Get users count
    users_count = await session.execute(
        select(func.count(User.id)).where(User.gym_id == gym_id)
    )
    
    gym_dict = {
        "id": str(gym.id),  # Convert UUID to string
        "name": gym.name,
        "address": gym.address,
        "phone": gym.phone,
        "is_active": gym.is_active,
        "stats": {
            "branches_count": branches_count.scalar_one(),
            "members_count": members_count.scalar_one(),
            "users_count": users_count.scalar_one()
        }
    }
    
    return gym_dict

async def create_gym_db(
    session: AsyncSession,
    gym_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Create a new gym."""
    gym = Gym(**gym_data)
    session.add(gym)
    await session.commit()
    await session.refresh(gym)
    
    return await get_gym_with_related_data(session, str(gym.id))

async def update_gym_db(
    session: AsyncSession,
    gym_id: str,
    gym_data: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """Update a gym's details."""
    query = update(Gym).where(Gym.id == gym_id).values(**gym_data)
    result = await session.execute(query)
    await session.commit()
    
    if result.rowcount == 0:
        return None
        
    return await get_gym_with_related_data(session, gym_id)

async def get_branches_for_gym_db(
    session: AsyncSession,
    gym_id: str,
    page: int = 1,
    page_size: int = 50
) -> Dict[str, Any]:
    """Get all branches for a gym with pagination."""
    base_query = (
        select(Branch)
        .outerjoin(Branch.gym)  # Explicit join for 1.4
        .where(Branch.gym_id == gym_id)
    )
    
    # Get total count using subquery
    count_query = select(func.count(1)).select_from(base_query.subquery())
    total = await session.execute(count_query)
    total_branches = total.scalar_one()
    
    # Get paginated results
    offset = (page - 1) * page_size
    query = base_query.offset(offset).limit(page_size)
    result = await session.execute(query)
    branches = result.unique().scalars().all()  # Added unique()
    
    branches_data = [branch.to_dict() for branch in branches]
    
    return {
        "branches": branches_data,
        "pagination": {
            "total": total_branches,
            "page": page,
            "page_size": page_size,
            "pages": (total_branches + page_size - 1) // page_size
        }
    }

async def create_branch_db(
    session: AsyncSession,
    branch_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Create a new branch."""
    branch = Branch(**branch_data)
    session.add(branch)
    await session.commit()
    await session.refresh(branch)
    
    return branch.to_dict()

async def update_branch_db(
    session: AsyncSession,
    branch_id: str,
    branch_data: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """Update a branch's details."""
    query = update(Branch).where(Branch.id == branch_id).values(**branch_data)
    result = await session.execute(query)
    await session.commit()
    
    if result.rowcount == 0:
        return None
    
    # Get updated branch
    branch_query = select(Branch).where(Branch.id == branch_id)
    result = await session.execute(branch_query)
    branch = result.scalar_one_or_none()
    
    return branch.to_dict() if branch else None

async def get_members_for_branch_db(
    session: AsyncSession,
    branch_id: str,
    page: int = 1,
    page_size: int = 50
) -> Dict[str, Any]:
    """Get all members for a branch with pagination."""
    base_query = select(Member).where(Member.branch_id == branch_id)
    
    # Get total count
    count_query = select(func.count()).select_from(base_query.subquery())
    total = await session.execute(count_query)
    total_members = total.scalar_one()
    
    # Get paginated results
    offset = (page - 1) * page_size
    query = base_query.offset(offset).limit(page_size)
    result = await session.execute(query)
    members = result.scalars().all()
    
    members_data = [member.to_dict() for member in members]
    
    return {
        "members": members_data,
        "pagination": {
            "total": total_members,
            "page": page,
            "page_size": page_size,
            "pages": (total_members + page_size - 1) // page_size
        }
    }

async def create_member_db(
    session: AsyncSession,
    member_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Create a new member."""
    member = Member(**member_data)
    session.add(member)
    await session.commit()
    await session.refresh(member)
    
    return member.to_dict()

async def update_member_db(
    session: AsyncSession,
    member_id: str,
    member_data: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """Update a member's details."""
    query = update(Member).where(Member.id == member_id).values(**member_data)
    result = await session.execute(query)
    await session.commit()
    
    if result.rowcount == 0:
        return None
    
    # Get updated member
    member_query = select(Member).where(Member.id == member_id)
    result = await session.execute(member_query)
    member = result.scalar_one_or_none()
    
    return member.to_dict() if member else None

async def get_users_for_branch_db(
    session: AsyncSession,
    branch_id: str,
    page: int = 1,
    page_size: int = 50
) -> Dict[str, Any]:
    """Get all users for a branch with pagination."""
    base_query = select(User).where(User.branch_id == branch_id)
    
    # Get total count
    count_query = select(func.count()).select_from(base_query.subquery())
    total = await session.execute(count_query)
    total_users = total.scalar_one()
    
    # Get paginated results
    offset = (page - 1) * page_size
    query = base_query.offset(offset).limit(page_size)
    result = await session.execute(query)
    users = result.scalars().all()
    
    users_data = [user.to_dict() for user in users]
    
    return {
        "users": users_data,
        "pagination": {
            "total": total_users,
            "page": page,
            "page_size": page_size,
            "pages": (total_users + page_size - 1) // page_size
        }
    }

async def create_user_db(
    session: AsyncSession,
    user_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Create a new user."""
    user = User(**user_data)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    
    return user.to_dict()

async def update_user_db(
    session: AsyncSession,
    user_id: str,
    user_data: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """Update a user's details."""
    query = update(User).where(User.id == user_id).values(**user_data)
    result = await session.execute(query)
    await session.commit()
    
    if result.rowcount == 0:
        return None
    
    # Get updated user
    user_query = select(User).where(User.id == user_id)
    result = await session.execute(user_query)
    user = result.scalar_one_or_none()
    
    return user.to_dict() if user else None

async def assign_user_to_branch_db(
    session: AsyncSession,
    user_id: str,
    branch_id: str
) -> bool:
    """Assign a user to a branch."""
    user_query = select(User).where(User.id == user_id)
    result = await session.execute(user_query)
    user = result.scalar_one_or_none()
    
    if not user:
        return False
    
    branch_query = select(Branch).where(Branch.id == branch_id)
    result = await session.execute(branch_query)
    branch = result.scalar_one_or_none()
    
    if not branch:
        return False
    
    user.branches.append(branch)
    await session.commit()
    
    return True

async def remove_user_from_branch_db(
    session: AsyncSession,
    user_id: str,
    branch_id: str
) -> bool:
    """Remove a user from a branch."""
    user_query = select(User).where(User.id == user_id)
    result = await session.execute(user_query)
    user = result.scalar_one_or_none()
    
    if not user:
        return False
    
    branch_query = select(Branch).where(Branch.id == branch_id)
    result = await session.execute(branch_query)
    branch = result.scalar_one_or_none()
    
    if not branch:
        return False
    
    user.branches.remove(branch)
    await session.commit()
    
    return True

async def delete_gym_db(
    session: AsyncSession,
    gym_id: str
) -> bool:
    """Delete a gym with cascade."""
    logger.info(f"Deleting gym with ID: {gym_id}")
    
    try:
        # First delete related records
        # Delete branches
        branches_query = select(Branch).where(Branch.gym_id == gym_id)
        branches_result = await session.execute(branches_query)
        branches = branches_result.scalars().all()
        
        for branch in branches:
            # Delete branch-specific settings
            settings_queries = [
                delete(GymSettings).where(GymSettings.branch_id == branch.id),
                delete(CallSettings).where(CallSettings.branch_id == branch.id),
                delete(AISettings).where(AISettings.branch_id == branch.id),
                delete(VoiceSettings).where(VoiceSettings.branch_id == branch.id)
            ]
            
            for query in settings_queries:
                await session.execute(query.execution_options(synchronize_session="fetch"))
            
            # Delete branch
            await session.execute(
                delete(Branch)
                .where(Branch.id == branch.id)
                .execution_options(synchronize_session="fetch")
            )
        
        # Delete gym
        gym_query = (
            delete(Gym)
            .where(Gym.id == gym_id)
            .execution_options(synchronize_session="fetch")
        )
        result = await session.execute(gym_query)
        await session.commit()
        
        return result.rowcount > 0
        
    except Exception as e:
        await session.rollback()
        logger.error(f"Error deleting gym {gym_id}: {str(e)}")
        raise

async def delete_branch_db(
    session: AsyncSession,
    branch_id: str
) -> bool:
    """Delete a branch with cascade."""
    logger.info(f"Deleting branch with ID: {branch_id}")
    
    try:
        # First delete related settings
        settings_queries = [
            delete(GymSettings).where(GymSettings.branch_id == branch_id),
            delete(CallSettings).where(CallSettings.branch_id == branch_id),
            delete(AISettings).where(AISettings.branch_id == branch_id),
            delete(VoiceSettings).where(VoiceSettings.branch_id == branch_id)
        ]
        
        for query in settings_queries:
            await session.execute(query.execution_options(synchronize_session="fetch"))
        
        # Delete branch
        branch_query = (
            delete(Branch)
            .where(Branch.id == branch_id)
            .execution_options(synchronize_session="fetch")
        )
        result = await session.execute(branch_query)
        await session.commit()
        
        return result.rowcount > 0
        
    except Exception as e:
        await session.rollback()
        logger.error(f"Error deleting branch {branch_id}: {str(e)}")
        raise

async def delete_member_db(
    session: AsyncSession,
    member_id: str
) -> bool:
    """Delete a member with cascade."""
    logger.info(f"Deleting member with ID: {member_id}")
    
    try:
        query = (
            delete(Member)
            .where(Member.id == member_id)
            .execution_options(synchronize_session="fetch")
        )
        result = await session.execute(query)
        await session.commit()
        
        return result.rowcount > 0
        
    except Exception as e:
        await session.rollback()
        logger.error(f"Error deleting member {member_id}: {str(e)}")
        raise

async def delete_user_db(
    session: AsyncSession,
    user_id: str
) -> bool:
    """Delete a user with cascade."""
    logger.info(f"Deleting user with ID: {user_id}")
    
    try:
        # First remove user from branches (many-to-many relationship)
        await session.execute(
            delete(user_branch)
            .where(user_branch.c.user_id == user_id)
            .execution_options(synchronize_session="fetch")
        )
        
        # Delete user
        query = (
            delete(User)
            .where(User.id == user_id)
            .execution_options(synchronize_session="fetch")
        )
        result = await session.execute(query)
        await session.commit()
        
        return result.rowcount > 0
        
    except Exception as e:
        await session.rollback()
        logger.error(f"Error deleting user {user_id}: {str(e)}")
        raise