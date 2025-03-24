"""
AISettings model for storing AI-specific settings for automated calls.
"""
from sqlalchemy import Column, String, Boolean, Integer, DateTime, ForeignKey
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship
from uuid import uuid4

from ..base import Base

class AISettings(Base):
    """AISettings model for storing AI-specific settings for automated calls."""
    
    __tablename__ = "ai_settings"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    gym_id = Column(String(36), ForeignKey("gyms.id"), nullable=False)
    branch_id = Column(String(36), ForeignKey("branches.id"), nullable=False, unique=True)
    personality = Column(String(100), nullable=False)
    agent_name = Column(String(100), nullable=False)
    greeting = Column(String(255), nullable=True)
    allow_interruptions = Column(Boolean, default=True, nullable=False)
    offer_human_transfer = Column(Boolean, default=True, nullable=False)
    escalation_threshold = Column(Integer, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True),nullable=False,server_default=text('now()'))
    updated_at = Column(TIMESTAMP(timezone=True),nullable=False,server_default=text('now()'),onupdate=text('now()'))
    
    # Relationships
    gym = relationship("Gym", back_populates="ai_settings")
    branch = relationship("Branch", back_populates="ai_settings")
    
    def to_dict(self):
        """Convert the model instance to a dictionary."""
        return {
            "id": self.id,
            "gym_id": self.gym_id,
            "branch_id": self.branch_id,
            "personality": self.personality,
            "agent_name": self.agent_name,
            "greeting": self.greeting,
            "allow_interruptions": self.allow_interruptions,
            "offer_human_transfer": self.offer_human_transfer,
            "escalation_threshold": self.escalation_threshold,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        } 