"""
CallSettings model for storing call-specific settings for a branch.
"""
from sqlalchemy import Column, String, Boolean, Integer, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text
from uuid import uuid4
from sqlalchemy.dialects.postgresql import UUID
from ..base import Base

class CallSettings(Base):
    """CallSettings model for storing call-specific settings for a branch."""
    
    __tablename__ = "call_settings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    branch_id = Column(UUID(as_uuid=True), ForeignKey("branches.id"), nullable=False, unique=True)
    gym_id = Column(UUID(as_uuid=True), ForeignKey("gyms.id"), nullable=False)
    max_duration = Column(Integer, nullable=True)  # in seconds
    call_hours_start = Column(String(10), nullable=True)  # HH:MM format
    call_hours_end = Column(String(10), nullable=True)  # HH:MM format
    active_call_days = Column(Text, nullable=True)  # JSON array of days: ["Monday", "Tuesday", ...]
    retry_attempts = Column(Integer, nullable=True)
    retry_interval = Column(Integer, nullable=True)  # in hours
    do_not_disturb = Column(Boolean, default=False, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),nullable=False,server_default=text('now()'))
    updated_at = Column(TIMESTAMP(timezone=True),nullable=False,server_default=text('now()'),onupdate=text('now()'))
    
    def to_dict(self):
        """Convert the model instance to a dictionary."""
        return {
            "id": self.id,
            "branch_id": self.branch_id,
            "gym_id": self.gym_id,
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

from backend.db.models.gym.branch import Branch
from backend.db.models.gym.gym import Gym

CallSettings.branch = relationship("Branch", back_populates="call_settings")
CallSettings.gym = relationship("Gym", back_populates="call_settings")