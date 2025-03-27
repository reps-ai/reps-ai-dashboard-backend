import uuid
from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from ...base import Base

class Gym(Base):
    __tablename__ = "gyms"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    address = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Removed inline relationships:
    # branches = relationship("Branch", back_populates="gym")
    # users = relationship("User", back_populates="gym")
    # members = relationship("Member", back_populates="gym")
    # appointments = relationship("Appointment", back_populates="gym")
    # voice_settings = relationship("VoiceSettings", back_populates="gym")
    # ai_settings = relationship("AISettings", back_populates="gym")
    # leads = relationship("Lead", back_populates="gym")
    # call_logs = relationship("CallLog", back_populates="gym")
    # follow_up_campaign = relationship("FollowUpCampaign", back_populates="gym")
    # follow_up_calls = relationship("FollowUpCall", back_populates="gym")

Gym.branches = relationship("Branch", back_populates="gym")
Gym.users = relationship("User", back_populates="gym")
Gym.members = relationship("Member", back_populates="gym")
Gym.appointments = relationship("Appointment", back_populates="gym")
Gym.voice_settings = relationship("VoiceSettings", back_populates="gym")
Gym.ai_settings = relationship("AISettings", back_populates="gym")
Gym.leads = relationship("Lead", back_populates="gym")
Gym.call_logs = relationship("CallLog", back_populates="gym")
Gym.follow_up_campaign = relationship("FollowUpCampaign", back_populates="gym")
Gym.follow_up_calls = relationship("FollowUpCall", back_populates="gym")