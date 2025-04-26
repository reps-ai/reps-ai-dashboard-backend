"""
Factory for creating Analytics Service instances.
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.repositories.analytics.interface import AnalyticsRepository
from backend.db.repositories.analytics.implementations.postgres_analytics_repository import PostgresAnalyticsRepository
from backend.services.analytics.interface import AnalyticsService
from backend.services.analytics.implementation import DefaultAnalyticsService

def create_analytics_service(session: AsyncSession) -> AnalyticsService:
    """
    Create a configured Analytics Service.
    
    Args:
        session: Database session
        
    Returns:
        Configured Analytics Service instance
    """
    # Create the repository
    repository = PostgresAnalyticsRepository(session)
    
    # Create the service with the repository
    service = DefaultAnalyticsService(repository)
    
    return service
