"""
Branch model for storing gym branch information.
"""
from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text
from uuid import uuid4
from sqlalchemy.dialects.postgresql import UUID

from ...base import Base

class Branch(Base):
    """Branch model for storing gym branch information."""
    
    __tablename__ = "branches"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    gym_id = Column(UUID(as_uuid=True), ForeignKey("gyms.id"), nullable=True)
    name = Column(String(255), nullable=False)
    address = Column(Text, nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),nullable=False,server_default=text('now()'))
    updated_at = Column(TIMESTAMP(timezone=True),nullable=False,server_default=text('now()'),onupdate=text('now()'))
    
    def to_dict(self):
        """Convert the model instance to a dictionary."""
        return {
            "id": self.id,
            "gym_id": self.gym_id,
            "name": self.name,
            "address": self.address,
            "phone": self.phone,
            "email": self.email,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

# Import dependent models to ensure registration:
from backend.db.models.gym.gym import Gym
from backend.db.models.lead.lead import Lead
from backend.db.models.appointment import Appointment
from backend.db.models.member import Member
from backend.db.models.campaign.follow_up_campaign import FollowUpCampaign
from backend.db.models.voice_settings import VoiceSettings
from backend.db.models.ai_settings import AISettings
from backend.db.models.call.call_settings import CallSettings
from backend.db.models.gym.knowledge_base import KnowledgeBase
from backend.db.models.user import User
from backend.db.models.gym.gym_settings import GymSettings

# Define relationships AFTER the class is defined:
Branch.gym = relationship("Gym", back_populates="branches")
Branch.leads = relationship("Lead", back_populates="branch")
Branch.appointments = relationship("Appointment", back_populates="branch")
Branch.members = relationship("Member", back_populates="branch")
Branch.follow_up_campaigns = relationship("FollowUpCampaign", back_populates="branch")
Branch.voice_settings = relationship("VoiceSettings", back_populates="branch", uselist=False)
Branch.ai_settings = relationship("AISettings", back_populates="branch", uselist=False)
Branch.call_settings = relationship("CallSettings", back_populates="branch", uselist=False)
Branch.knowledge_base = relationship("KnowledgeBase", back_populates="branch")
Branch.users = relationship("User", secondary="user_branch", back_populates="branches")
Branch.call_logs = relationship("CallLog", back_populates="branch")
Branch.follow_up_calls = relationship("FollowUpCall", back_populates="branch")
Branch.gym_settings = relationship("GymSettings", back_populates="branch", uselist=False)