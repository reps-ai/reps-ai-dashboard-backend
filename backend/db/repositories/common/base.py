"""
Base repository interface for database access.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, TypeVar, Generic

T = TypeVar('T')

class BaseRepository(Generic[T], ABC):
    """
    Base repository interface for database access.
    """
    
    @abstractmethod
    async def create(self, data: Dict[str, Any]) -> T:
        """
        Create a new entity.
        
        Args:
            data: Dictionary containing entity data
            
        Returns:
            Created entity
        """
        pass
    
    @abstractmethod
    async def get(self, entity_id: str) -> Optional[T]:
        """
        Get an entity by ID.
        
        Args:
            entity_id: ID of the entity
            
        Returns:
            Entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def update(self, entity_id: str, data: Dict[str, Any]) -> Optional[T]:
        """
        Update an entity.
        
        Args:
            entity_id: ID of the entity
            data: Dictionary containing updated entity data
            
        Returns:
            Updated entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def delete(self, entity_id: str) -> bool:
        """
        Delete an entity.
        
        Args:
            entity_id: ID of the entity
            
        Returns:
            True if deletion was successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def list(self, filters: Optional[Dict[str, Any]] = None) -> List[T]:
        """
        List entities with optional filtering.
        
        Args:
            filters: Optional filters for the entities
            
        Returns:
            List of entities matching the criteria
        """
        pass 