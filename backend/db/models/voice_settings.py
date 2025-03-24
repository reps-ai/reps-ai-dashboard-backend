"""
VoiceSettings model for storing voice-specific settings for AI calls.
"""
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship
from uuid import uuid4

from ..base import Base

class VoiceSettings(Base):
    """VoiceSettings model for storing voice-specific settings for AI calls."""
    
    __tablename__ = "voice_settings"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    gym_id = Column(String(36), ForeignKey("gyms.id"), nullable=False)
    branch_id = Column(String(36), ForeignKey("branches.id"), nullable=False, unique=True)
    voice_type = Column(String(100), nullable=False)
    speaking_speed = Column(String(50), nullable=True)
    volume = Column(String(50), nullable=True)
    voice_sample_url = Column(String(255), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True),nullable=False,server_default=text('now()'))
    updated_at = Column(TIMESTAMP(timezone=True),nullable=False,server_default=text('now()'),onupdate=text('now()'))
    
    def to_dict(self):
        """Convert the model instance to a dictionary."""
        return {
            "id": self.id,
            "gym_id": self.gym_id,
            "branch_id": self.branch_id,
            "voice_type": self.voice_type,
            "speaking_speed": self.speaking_speed,
            "volume": self.volume,
            "voice_sample_url": self.voice_sample_url,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

from backend.db.models.gym.gym import Gym
from backend.db.models.gym.branch import Branch

VoiceSettings.gym = relationship("Gym", back_populates="voice_settings")
VoiceSettings.branch = relationship("Branch", back_populates="voice_settings")