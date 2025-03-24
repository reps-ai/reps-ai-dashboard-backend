"""
Factory for creating lead service instances.
"""
from sqlalchemy.ext.asyncio import AsyncSession

from .interface import LeadService
from .implementation import DefaultLeadService
from ...db.repositories.lead import LeadRepository
from ...db.repositories.lead.implementations import PostgresLeadRepository

class LeadServiceFactory:
    """
    Factory for creating lead service instances.
    """
    
    @staticmethod
    async def create_service(session: AsyncSession) -> LeadService:
        """
        Create a lead service instance.
        
        Args:
            session: Database session
            
        Returns:
            Lead service instance
        """
        # Create repository
        lead_repository = PostgresLeadRepository(session)
        
        # Create service
        return DefaultLeadService(lead_repository) 