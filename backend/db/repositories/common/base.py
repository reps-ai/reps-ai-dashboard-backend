"""
Base repository interface that defines common operations for all repositories.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TypeVar, Generic

T = TypeVar('T')

class BaseRepository(ABC, Generic[T]):
    """
    Abstract base class defining common operations for all repositories.
    This provides a consistent interface for basic CRUD operations.
    """
    
    @abstractmethod
    async def create(self, data: Dict[str, Any]) -> T:
        """
        Create a new entity.

        Args:
            data: Dictionary containing entity data

        Returns:
            The created entity
        """
        pass

    @abstractmethod
    async def get_by_id(self, entity_id: str) -> Optional[T]:
        """
        Get an entity by ID.

        Args:
            entity_id: Unique identifier of the entity

        Returns:
            The entity if found, None otherwise
        """
        pass

    @abstractmethod
    async def update(self, entity_id: str, data: Dict[str, Any]) -> Optional[T]:
        """
        Update an entity.

        Args:
            entity_id: Unique identifier of the entity
            data: Dictionary containing updated entity data

        Returns:
            The updated entity if successful, None if entity not found
        """
        pass

    @abstractmethod
    async def delete(self, entity_id: str) -> bool:
        """
        Delete an entity.

        Args:
            entity_id: Unique identifier of the entity

        Returns:
            True if deleted successfully, False otherwise
        """
        pass

    @abstractmethod
    async def list(self, filters: Optional[Dict[str, Any]] = None) -> List[T]:
        """
        List entities with optional filtering.

        Args:
            filters: Optional dictionary of filter criteria

        Returns:
            List of entities matching the criteria
        """
        pass

    @abstractmethod
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count entities with optional filtering.

        Args:
            filters: Optional dictionary of filter criteria

        Returns:
            Count of entities matching the criteria
        """
        pass

    @abstractmethod
    async def exists(self, entity_id: str) -> bool:
        """
        Check if an entity exists.

        Args:
            entity_id: Unique identifier of the entity

        Returns:
            True if entity exists, False otherwise
        """
        pass 