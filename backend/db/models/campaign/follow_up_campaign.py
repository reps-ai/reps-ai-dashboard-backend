"""
FollowUpCampaign model for tracking campaigns to follow up with leads.
"""
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text
from uuid import uuid4
from sqlalchemy.dialects.postgresql import UUID

from ...base import Base

class FollowUpCampaign(Base):
    """FollowUpCampaign model for tracking campaigns to follow up with leads."""
    
    __tablename__ = "follow_up_campaigns"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id"), nullable=False)
    gym_id = Column(UUID(as_uuid=True), ForeignKey("gyms.id"), nullable=False)
    branch_id = Column(UUID(as_uuid=True), ForeignKey("branches.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    frequency = Column(Integer, nullable=False)  # Frequency of follow-ups in days
    gap = Column(Integer, nullable=False)  # Gap between follow-ups in days
    campaign_status = Column(String(50), nullable=False)  # active, completed, paused, cancelled
    created_at = Column(TIMESTAMP(timezone=True),nullable=False,server_default=text('now()'))
    updated_at = Column(TIMESTAMP(timezone=True),nullable=False,server_default=text('now()'),onupdate=text('now()'))
    
    # Relationships
    lead = relationship("Lead", back_populates="follow_up_campaigns")
    branch = relationship("Branch", back_populates="follow_up_campaigns")
    gym = relationship("Gym", back_populates="follow_up_campaign")
    follow_up_calls = relationship("FollowUpCall", back_populates="follow_up_campaign")
    call_logs = relationship("CallLog", back_populates="campaign", cascade="all")  # Changed from "all, delete-orphan" to just "all"
    
    def to_dict(self):
        """Convert the model instance to a dictionary."""
        return {
            "id": self.id,
            "lead_id": self.lead_id,
            "gym_id": self.gym_id,
            "branch_id": self.branch_id,
            "name": self.name,
            "description": self.description,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "period": self.frequency,
            "gap": self.gap,
            "campaign_status": self.campaign_status,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

# Import dependent models to ensure registration:
from backend.db.models.call.call_log import CallLog
from backend.db.models.lead.lead import Lead
from backend.db.models.call.follow_up_call import FollowUpCall
from backend.db.models.gym.gym import Gym
from backend.db.models.gym.branch import Branch

FollowUpCampaign.call_logs = relationship("CallLog", back_populates="campaign")
FollowUpCampaign.lead = relationship("Lead", back_populates="follow_up_campaigns")
FollowUpCampaign.follow_up_calls = relationship("FollowUpCall", back_populates="campaign")
FollowUpCampaign.gym = relationship("Gym", back_populates="follow_up_campaign")
FollowUpCampaign.branch = relationship("Branch", back_populates="follow_up_campaigns")