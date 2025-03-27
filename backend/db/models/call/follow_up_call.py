"""
FollowUpCall model for tracking follow-up calls made as part of campaigns.
"""
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text
from uuid import uuid4

from ..base import Base

class FollowUpCall(Base):
    """FollowUpCall model for tracking follow-up calls made as part of campaigns."""
    
    __tablename__ = "follow_up_calls"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    lead_id = Column(String(36), ForeignKey("leads.id"), nullable=False)
    branch_id = Column(String(36), ForeignKey("branches.id"), nullable=False)
    gym_id = Column(String(36), ForeignKey("gyms.id"), nullable=False)
    campaign_id = Column(String(36), ForeignKey("follow_up_campaigns.id"), nullable=False)
    number_of_calls = Column(Integer, nullable=True)
    call_date_time = Column(DateTime, nullable=False)
    duration = Column(Integer, nullable=True)  # in seconds
    call_type = Column(String(50), nullable=False)  # outbound, inbound, ai, etc.
    human_notes = Column(Text, nullable=True)
    outcome = Column(String(50), nullable=True)  # scheduled, not_interested, callback, etc.
    call_status = Column(String(50), nullable=False)  # scheduled, in_progress, completed, failed, etc.
    recording_url = Column(String(255), nullable=True)
    transcript = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    sentiment = Column(String(50), nullable=True)  # positive, negative, neutral
    created_at = Column(TIMESTAMP(timezone=True),nullable=False,server_default=text('now()'))
    updated_at = Column(TIMESTAMP(timezone=True),nullable=False,server_default=text('now()'),onupdate=text('now()'))
    
    def to_dict(self):
        """Convert the model instance to a dictionary."""
        return {
            "id": self.id,
            "lead_id": self.lead_id,
            "branch_id": self.branch_id,
            "gym_id": self.gym_id,
            "campaign_id": self.campaign_id,
            "number_of_calls": self.number_of_calls,
            "call_date_time": self.call_date_time,
            "duration": self.duration,
            "call_type": self.call_type,
            "human_notes": self.human_notes,
            "outcome": self.outcome,
            "call_status": self.call_status,
            "recording_url": self.recording_url,
            "transcript": self.transcript,
            "summary": self.summary,
            "sentiment": self.sentiment,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

from backend.db.models.lead.lead import Lead
from backend.db.models.campaign.follow_up_campaign import FollowUpCampaign
from backend.db.models.gym.branch import Branch
from backend.db.models.gym.gym import Gym

FollowUpCall.lead = relationship("Lead", back_populates="follow_up_calls")
FollowUpCall.campaign = relationship("FollowUpCampaign", back_populates="follow_up_calls")
FollowUpCall.branch = relationship("Branch", back_populates="follow_up_calls")
FollowUpCall.gym = relationship("Gym", back_populates="follow_up_calls")