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
    
    # Relationships
    branches = relationship("Branch", back_populates="gym")
    users = relationship("User", back_populates="gym")
    members = relationship("Member", back_populates="gym")
    appointments = relationship("Appointment", back_populates="gym")
    voice_settings = relationship("VoiceSettings", back_populates="gym")
    ai_settings = relationship("AISettings", back_populates="gym") 