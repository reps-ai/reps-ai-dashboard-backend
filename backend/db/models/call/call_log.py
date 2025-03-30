"""
CallLog model for tracking calls made to leads.
"""
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text
from uuid import uuid4
from sqlalchemy.dialects.postgresql import UUID
from ..base import Base

class CallLog(Base):
    """CallLog model for tracking calls made to leads."""
    
    __tablename__ = "call_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    branch_id = Column(UUID(as_uuid=True), ForeignKey("branches.id"), nullable=False)
    gym_id = Column(UUID(as_uuid=True), ForeignKey("gyms.id"), nullable=False)
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id"), nullable=False)
    duration = Column(Integer, nullable=True)  # in seconds
    call_type = Column(String(50), nullable=False)  # outbound or inbound
    human_notes = Column(Text, nullable=True)
    outcome = Column(String(50), nullable=True)  # scheduled, not_interested, callback, etc.
    created_at = Column(TIMESTAMP(timezone=True),nullable=False,server_default=text('now()'))
    updated_at = Column(TIMESTAMP(timezone=True),nullable=False,server_default=text('now()'),onupdate=text('now()'))
    call_status = Column(String(50), nullable=False)  # completed, failed, etc.
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    recording_url = Column(String(255), nullable=True)
    transcript = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    sentiment = Column(String(50), nullable=True)  # positive, negative, neutral
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("follow_up_campaigns.id"), nullable=True)  # Changed to nullable=True
    
    def to_dict(self):
        """Convert the model instance to a dictionary."""
        return {
            "id": self.id,
            "lead_id": self.lead_id,
            "branch_id": self.branch_id,
            "gym_id": self.gym_id,
            "duration": self.duration,
            "call_type": self.call_type,
            "human_notes": self.human_notes,
            "outcome": self.outcome,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "call_status": self.call_status,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "recording_url": self.recording_url,
            "transcript": self.transcript,
            "summary": self.summary,
            "sentiment": self.sentiment,
            "campaign_id": self.campaign_id
        }

from backend.db.models.lead.lead import Lead
from backend.db.models.gym.branch import Branch
from backend.db.models.gym.gym import Gym
from backend.db.models.campaign.follow_up_campaign import FollowUpCampaign

CallLog.lead = relationship("Lead", back_populates="call_logs")
CallLog.branch = relationship("Branch", back_populates="call_logs")
CallLog.gym = relationship("Gym", back_populates="call_logs")
CallLog.campaign = relationship("FollowUpCampaign", back_populates="call_logs")