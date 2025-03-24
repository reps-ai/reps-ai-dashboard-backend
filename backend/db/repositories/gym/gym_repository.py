"""
Gym repository interface defining the contract for gym operations.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime

class GymRepository(ABC):
    """
    Abstract base class defining the interface for gym repository operations.
    Any concrete implementation must implement all these methods.
    """
    
    @abstractmethod
    async def create_gym(self, gym_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new gym.

        Args:
            gym_data: Dictionary containing gym details

        Returns:
            Dict containing the created gym data
        """
        pass

    @abstractmethod
    async def get_gym_by_id(self, gym_id: str) -> Optional[Dict[str, Any]]:
        """
        Get gym details by ID.

        Args:
            gym_id: Unique identifier of the gym

        Returns:
            Gym data if found, None otherwise
        """
        pass

    @abstractmethod
    async def update_gym(self, gym_id: str, gym_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update gym details.

        Args:
            gym_id: Unique identifier of the gym
            gym_data: Dictionary containing updated gym details

        Returns:
            Updated gym data if successful, None if gym not found
        """
        pass

    @abstractmethod
    async def delete_gym(self, gym_id: str) -> bool:
        """
        Delete a gym.

        Args:
            gym_id: Unique identifier of the gym

        Returns:
            True if deleted successfully, False otherwise
        """
        pass

    @abstractmethod
    async def get_all_gyms(self) -> List[Dict[str, Any]]:
        """
        Get all gyms.

        Returns:
            List of all gym data
        """
        pass

    @abstractmethod
    async def get_gym_settings(self, gym_id: str) -> Optional[Dict[str, Any]]:
        """
        Get settings for a gym.

        Args:
            gym_id: Unique identifier of the gym

        Returns:
            Gym settings data if found, None otherwise
        """
        pass

    @abstractmethod
    async def update_gym_settings(self, gym_id: str, settings: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update settings for a gym.

        Args:
            gym_id: Unique identifier of the gym
            settings: Dictionary containing updated settings

        Returns:
            Updated gym settings data if successful, None if gym not found
        """
        pass

    @abstractmethod
    async def get_gym_users(self, gym_id: str) -> List[Dict[str, Any]]:
        """
        Get all users associated with a gym.

        Args:
            gym_id: Unique identifier of the gym

        Returns:
            List of user data associated with the gym
        """
        pass

    @abstractmethod
    async def add_user_to_gym(self, gym_id: str, user_id: str, role: str) -> bool:
        """
        Add a user to a gym with a specific role.

        Args:
            gym_id: Unique identifier of the gym
            user_id: Unique identifier of the user
            role: Role of the user in the gym

        Returns:
            True if user was added successfully, False otherwise
        """
        pass

    @abstractmethod
    async def remove_user_from_gym(self, gym_id: str, user_id: str) -> bool:
        """
        Remove a user from a gym.

        Args:
            gym_id: Unique identifier of the gym
            user_id: Unique identifier of the user

        Returns:
            True if user was removed successfully, False otherwise
        """
        pass

    @abstractmethod
    async def update_user_role(self, gym_id: str, user_id: str, role: str) -> bool:
        """
        Update a user's role in a gym.

        Args:
            gym_id: Unique identifier of the gym
            user_id: Unique identifier of the user
            role: New role of the user

        Returns:
            True if role was updated successfully, False otherwise
        """
        pass

    @abstractmethod
    async def get_gym_api_keys(self, gym_id: str) -> List[Dict[str, Any]]:
        """
        Get all API keys for a gym.

        Args:
            gym_id: Unique identifier of the gym

        Returns:
            List of API key data for the gym
        """
        pass

    @abstractmethod
    async def create_gym_api_key(self, gym_id: str, key_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new API key for a gym.

        Args:
            gym_id: Unique identifier of the gym
            key_data: Dictionary containing API key details

        Returns:
            Dict containing the created API key data
        """
        pass

    @abstractmethod
    async def revoke_gym_api_key(self, gym_id: str, key_id: str) -> bool:
        """
        Revoke an API key for a gym.

        Args:
            gym_id: Unique identifier of the gym
            key_id: Unique identifier of the API key

        Returns:
            True if key was revoked successfully, False otherwise
        """
        pass 