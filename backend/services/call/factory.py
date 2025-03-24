"""
Factory for creating call service instances.
"""
from sqlalchemy.ext.asyncio import AsyncSession

from .interface import CallService
from .implementation import DefaultCallService
from ...db.repositories.call import CallRepository
from ...db.repositories.call.implementations.postgres_call_repository import PostgresCallRepository

class CallServiceFactory:
    """Factory for creating call service instances."""
    
    @staticmethod
    async def create_service(session: AsyncSession) -> CallService:
        """
        Create a call service instance.
        
        Args:
            session: Database session
            
        Returns:
            Call service instance
        """
        # Create repository
        call_repository = PostgresCallRepository(session)
        
        # Create service
        return DefaultCallService(call_repository) 