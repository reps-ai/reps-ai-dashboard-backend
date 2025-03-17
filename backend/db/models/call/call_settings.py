"""
CallSettings model for storing call-specific settings for a branch.
"""
from sqlalchemy import Column, String, Boolean, Integer, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from uuid import uuid4

from ..base import Base

class CallSettings(Base):
    """CallSettings model for storing call-specific settings for a branch."""
    
    __tablename__ = "call_settings"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    branch_id = Column(String(36), ForeignKey("branches.id"), nullable=False, unique=True)
    max_duration = Column(Integer, nullable=True)  # in seconds
    call_hours_start = Column(String(10), nullable=True)  # HH:MM format
    call_hours_end = Column(String(10), nullable=True)  # HH:MM format
    active_call_days = Column(Text, nullable=True)  # JSON array of days: ["Monday", "Tuesday", ...]
    retry_attempts = Column(Integer, nullable=True)
    retry_interval = Column(Integer, nullable=True)  # in hours
    do_not_disturb = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    branch = relationship("Branch", back_populates="call_settings")
    
    def to_dict(self):
        """Convert the model instance to a dictionary."""
        return {
            "id": self.id,
            "branch_id": self.branch_id,
            "max_duration": self.max_duration,
            "call_hours_start": self.call_hours_start,
            "call_hours_end": self.call_hours_end,
            "active_call_days": self.active_call_days,
            "retry_attempts": self.retry_attempts,
            "retry_interval": self.retry_interval,
            "do_not_disturb": self.do_not_disturb,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        } 