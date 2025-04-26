"""
Lead Performance Analytics model for tracking lead metrics.
"""
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from uuid import uuid4
from sqlalchemy.dialects.postgresql import UUID
from ...base import Base

class LeadPerformanceAnalytics(Base):
    """Model for storing lead performance analytics data."""
    
    __tablename__ = "lead_performance_analytics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    branch_id = Column(UUID(as_uuid=True), ForeignKey("branches.id"), nullable=False)
    gym_id = Column(UUID(as_uuid=True), ForeignKey("gyms.id"), nullable=False)
    
    # Time dimensions
    date = Column(DateTime, nullable=False)
    period_type = Column(String(20), nullable=False)  # "daily", "weekly", "monthly"
    
    # Lead metrics
    total_lead_count = Column(Integer, nullable=False, default=0)
    new_lead_count = Column(Integer, nullable=False, default=0)
    contacted_lead_count = Column(Integer, nullable=False, default=0)
    qualified_lead_count = Column(Integer, nullable=False, default=0)
    converted_lead_count = Column(Integer, nullable=False, default=0)
    lost_lead_count = Column(Integer, nullable=False, default=0)
    
    # Conversion metrics
    conversion_rate = Column(Float, nullable=False, default=0.0)
    
    # Source metrics
    lead_source_distribution = Column(JSON, nullable=True)
    
    # Qualification metrics
    avg_qualification_score = Column(Float, nullable=True)
    
    # Growth metrics compared to previous period
    growth_metrics = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    def to_dict(self):
        """Convert the model instance to a dictionary."""
        return {
            "id": str(self.id),
            "branch_id": str(self.branch_id),
            "gym_id": str(self.gym_id),
            "date": self.date.isoformat() if self.date else None,
            "period_type": self.period_type,
            "total_lead_count": self.total_lead_count,
            "new_lead_count": self.new_lead_count,
            "contacted_lead_count": self.contacted_lead_count,
            "qualified_lead_count": self.qualified_lead_count,
            "converted_lead_count": self.converted_lead_count,
            "lost_lead_count": self.lost_lead_count,
            "conversion_rate": self.conversion_rate,
            "lead_source_distribution": self.lead_source_distribution,
            "avg_qualification_score": self.avg_qualification_score,
            "growth_metrics": self.growth_metrics,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

# Import models after class definition to avoid circular imports
from ...models.gym.gym import Gym
from ...models.gym.branch import Branch

# Define relationships
LeadPerformanceAnalytics.gym = relationship("Gym", back_populates="lead_performance_analytics")
LeadPerformanceAnalytics.branch = relationship("Branch", back_populates="lead_performance_analytics")
