"""
Call Performance Analytics model for tracking call metrics.
"""
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from uuid import uuid4
from sqlalchemy.dialects.postgresql import UUID
from ...base import Base

class CallPerformanceAnalytics(Base):
    """Model for storing call performance analytics data."""
    
    __tablename__ = "call_performance_analytics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    branch_id = Column(UUID(as_uuid=True), ForeignKey("branches.id"), nullable=False)
    gym_id = Column(UUID(as_uuid=True), ForeignKey("gyms.id"), nullable=False)
    
    # Time dimensions
    date = Column(DateTime, nullable=False)
    period_type = Column(String(20), nullable=False)  # "daily", "weekly", "monthly"
    
    # Call metrics
    total_call_count = Column(Integer, nullable=False, default=0)
    completed_call_count = Column(Integer, nullable=False, default=0)
    answered_call_count = Column(Integer, nullable=False, default=0)
    failed_call_count = Column(Integer, nullable=False, default=0)
    
    # Call outcomes
    outcome_distribution = Column(JSON, nullable=True)
    
    # Call durations
    avg_call_duration = Column(Float, nullable=True)  # in seconds
    min_call_duration = Column(Float, nullable=True)  # in seconds
    max_call_duration = Column(Float, nullable=True)  # in seconds
    
    # AI vs human comparison (if applicable)
    ai_call_count = Column(Integer, nullable=True, default=0)
    human_call_count = Column(Integer, nullable=True, default=0)
    ai_success_rate = Column(Float, nullable=True, default=0.0)
    human_success_rate = Column(Float, nullable=True, default=0.0)
    
    # Call insights
    call_insights = Column(JSON, nullable=True)
    
    # Pickup rate
    pickup_rate = Column(Float, nullable=False, default=0.0)
    
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
            "total_call_count": self.total_call_count,
            "completed_call_count": self.completed_call_count,
            "answered_call_count": self.answered_call_count,
            "failed_call_count": self.failed_call_count,
            "outcome_distribution": self.outcome_distribution,
            "avg_call_duration": self.avg_call_duration,
            "min_call_duration": self.min_call_duration,
            "max_call_duration": self.max_call_duration,
            "ai_call_count": self.ai_call_count,
            "human_call_count": self.human_call_count,
            "ai_success_rate": self.ai_success_rate,
            "human_success_rate": self.human_success_rate,
            "call_insights": self.call_insights,
            "pickup_rate": self.pickup_rate,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

# Import models after class definition to avoid circular imports
from ...models.gym.gym import Gym
from ...models.gym.branch import Branch

# Define relationships
CallPerformanceAnalytics.gym = relationship("Gym", back_populates="call_performance_analytics")
CallPerformanceAnalytics.branch = relationship("Branch", back_populates="call_performance_analytics")
