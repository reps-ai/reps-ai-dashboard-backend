"""
Cache invalidation utilities.
Provides functions to invalidate cache entries based on patterns or entity types.
"""

import asyncio
from typing import List, Optional, Union

from . import redis_client
from ..utils.logging.logger import get_logger

logger = get_logger(__name__)

async def invalidate_by_pattern(pattern: str) -> int:
    """
    Invalidate cache entries matching a pattern.
    
    Args:
        pattern: Redis key pattern to match
        
    Returns:
        Number of keys invalidated
    """
    if not redis_client:
        logger.warning("Redis client not available, skipping cache invalidation")
        return 0
        
    try:
        keys = await redis_client.keys(pattern)
        if keys:
            await redis_client.delete(*keys)
            logger.debug(f"Invalidated {len(keys)} cache keys matching pattern: {pattern}")
            return len(keys)
        return 0
    except Exception as e:
        logger.error(f"Error invalidating cache with pattern {pattern}: {str(e)}")
        return 0

async def invalidate_entity(entity_type: str, entity_id: str) -> int:
    """
    Invalidate all cache entries related to a specific entity.
    
    Args:
        entity_type: Type of entity (e.g., "lead", "user")
        entity_id: ID of the entity
        
    Returns:
        Number of keys invalidated
    """
    patterns = [
        f"{entity_type}:*{entity_id}*",            # Service cache
        f"{entity_type}_query:*{entity_id}*",      # Repository cache
        f"http:*{entity_type}*{entity_id}*"        # HTTP cache
    ]
    
    total_invalidated = 0
    for pattern in patterns:
        invalidated = await invalidate_by_pattern(pattern)
        total_invalidated += invalidated
        
    return total_invalidated

async def invalidate_lead(lead_id: str) -> int:
    """
    Invalidate all cache entries related to a specific lead.
    
    Args:
        lead_id: ID of the lead
        
    Returns:
        Number of keys invalidated
    """
    # Patterns specific to leads
    patterns = [
        f"lead:*{lead_id}*",                     # Lead service cache
        f"lead_query:*{lead_id}*",               # Lead repository cache
        f"http:*lead*{lead_id}*",                # HTTP cache for specific lead
        f"http:*leads*",                         # HTTP cache for lead lists
        f"leads:get_prioritized_leads*"          # Prioritized leads service cache
    ]
    
    total_invalidated = 0
    for pattern in patterns:
        invalidated = await invalidate_by_pattern(pattern)
        total_invalidated += invalidated
        
    return total_invalidated

async def invalidate_branch_leads(branch_id: str) -> int:
    """
    Invalidate all cache entries related to leads in a branch.
    
    Args:
        branch_id: ID of the branch
        
    Returns:
        Number of keys invalidated
    """
    patterns = [
        f"lead:*",                           # All lead service cache
        f"lead_query:*{branch_id}*",         # Lead repository cache with branch ID
        f"http:*lead*{branch_id}*",          # HTTP cache for leads by branch
        f"http:*leads/branch/{branch_id}*",  # HTTP cache for branch leads endpoint
        f"leads:get_prioritized_leads*"      # Prioritized leads service cache
    ]
    
    total_invalidated = 0
    for pattern in patterns:
        invalidated = await invalidate_by_pattern(pattern)
        total_invalidated += invalidated
        
    return total_invalidated 