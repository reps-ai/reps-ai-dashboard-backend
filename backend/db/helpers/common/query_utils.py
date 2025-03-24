"""
Common database query utilities.
"""
from typing import List, Dict, Any, Optional, Type, TypeVar, Union
from sqlalchemy import select, and_, or_, func, desc, update, delete, Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

from ...models.call.call_settings import CallSettings
from ...models.gym.gym_settings import GymSettings
from ...models.gym.knowledge_base import KnowledgeBase
from ...models.ai_settings import AISettings
from ...models.voice_settings import VoiceSettings
from ....utils.logging.logger import get_logger

logger = get_logger(__name__)

T = TypeVar('T', bound=DeclarativeBase)

async def get_settings_by_id(
    session: AsyncSession,
    model: Type[T],
    settings_id: str
) -> Optional[Dict[str, Any]]:
    """Get settings by ID."""
    query = select(model).where(model.id == settings_id)
    result = await session.execute(query)
    settings = result.unique().scalar_one_or_none()  # Added unique() for 1.4
    
    return settings.to_dict() if settings else None

async def get_settings_by_branch(
    session: AsyncSession,
    model: Type[T],
    branch_id: str
) -> Optional[Dict[str, Any]]:
    """Get settings by branch ID."""
    # Use explicit join for better 1.4 compatibility
    query = (
        select(model)
        .outerjoin(model.branch)
        .where(model.branch_id == branch_id)
    )
    result = await session.execute(query)
    settings = result.unique().scalar_one_or_none()
    
    return settings.to_dict() if settings else None

async def create_settings(
    session: AsyncSession,
    model: Type[T],
    settings_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Create new settings.
    
    Args:
        session: Database session
        model: Settings model class
        settings_data: Dictionary containing settings data
        
    Returns:
        Created settings data
    """
    settings = model(**settings_data)
    session.add(settings)
    await session.commit()
    await session.refresh(settings)
    
    return settings.to_dict()

async def update_settings(
    session: AsyncSession,
    model: Type[T],
    settings_id: str,
    settings_data: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    Update settings.
    
    Args:
        session: Database session
        model: Settings model class
        settings_id: Settings ID
        settings_data: Dictionary containing settings updates
        
    Returns:
        Updated settings data if successful, None if not found
    """
    query = (
        update(model)
        .where(model.id == settings_id)
        .values(**settings_data)
    )
    result = await session.execute(query)
    await session.commit()
    
    if result.rowcount == 0:
        return None
        
    return await get_settings_by_id(session, model, settings_id)

async def delete_settings(
    session: AsyncSession,
    model: Type[T],
    settings_id: str
) -> bool:
    """Delete settings with cascade."""
    try:
        # Add cascade delete options
        query = (
            delete(model)
            .where(model.id == settings_id)
            .execution_options(
                synchronize_session="fetch",
                enable_eagerloads=False
            )
        )
        result = await session.execute(query)
        await session.commit()
        
        return result.rowcount > 0
        
    except Exception as e:
        await session.rollback()
        logger.error(f"Error deleting settings {settings_id}: {str(e)}")
        raise

async def get_settings_by_gym(
    session: AsyncSession,
    model: Type[T],
    gym_id: str,
    page: int = 1,
    page_size: int = 50
) -> Dict[str, Any]:
    """Get all settings for a gym with pagination."""
    # Use explicit join for better 1.4 compatibility
    base_query = (
        select(model)
        .outerjoin(model.gym)
        .where(model.gym_id == gym_id)
    )
    
    # Get total count using subquery for 1.4 compatibility
    count_query = select(func.count(1)).select_from(base_query.subquery())
    total = await session.execute(count_query)
    total_settings = total.scalar_one()
    
    # Get paginated results
    offset = (page - 1) * page_size
    query = base_query.offset(offset).limit(page_size)
    result = await session.execute(query)
    settings = result.unique().scalars().all()  # Added unique() for relationships
    
    settings_data = [item.to_dict() for item in settings]
    
    return {
        "items": settings_data,
        "pagination": {
            "total": total_settings,
            "page": page,
            "page_size": page_size,
            "pages": (total_settings + page_size - 1) // page_size
        }
    }

# Knowledge Base specific queries
async def search_knowledge_base(
    session: AsyncSession,
    gym_id: str,
    search_term: str,
    tags: Optional[List[str]] = None,
    page: int = 1,
    page_size: int = 50
) -> Dict[str, Any]:
    """Search knowledge base items."""
    base_query = (
        select(KnowledgeBase)
        .outerjoin(KnowledgeBase.gym)  # Explicit join for 1.4
        .where(KnowledgeBase.gym_id == gym_id)
    )
    
    if search_term:
        base_query = base_query.where(
            or_(
                KnowledgeBase.question.ilike(f"%{search_term}%"),
                KnowledgeBase.answer.ilike(f"%{search_term}%")
            )
        )
    
    if tags:
        # Note: Using JSON operators in a more SQLAlchemy 1.4 friendly way
        for tag in tags:
            base_query = base_query.where(
                KnowledgeBase.tags.op('?')('tag')  # JSON contains operator
            )
    
    # Get total count using subquery
    count_query = select(func.count(1)).select_from(base_query.subquery())
    total = await session.execute(count_query)
    total_items = total.scalar_one()
    
    # Get paginated results with unique()
    offset = (page - 1) * page_size
    query = base_query.offset(offset).limit(page_size)
    result = await session.execute(query)
    items = result.unique().scalars().all()
    
    items_data = [item.to_dict() for item in items]
    
    return {
        "items": items_data,
        "pagination": {
            "total": total_items,
            "page": page,
            "page_size": page_size,
            "pages": (total_items + page_size - 1) // page_size
        }
    }