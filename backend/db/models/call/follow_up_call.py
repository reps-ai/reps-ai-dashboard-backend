"""
FollowUpCall model for tracking follow-up calls made as part of campaigns.
"""
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from uuid import uuid4

from ..base import Base

class FollowUpCall(Base):
    """FollowUpCall model for tracking follow-up calls made as part of campaigns."""
    
    __tablename__ = "follow_up_calls"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    lead_id = Column(String(36), ForeignKey("leads.id"), nullable=False)
    agent_user_id = Column(String(36), ForeignKey("users.id"), nullable=True)  # Null if AI call
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
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    lead = relationship("Lead", back_populates="follow_up_calls")
    agent = relationship("User", foreign_keys=[agent_user_id], back_populates="follow_up_calls")
    campaign = relationship("FollowUpCampaign", back_populates="follow_up_calls")
    
    def to_dict(self):
        """Convert the model instance to a dictionary."""
        return {
            "id": self.id,
            "lead_id": self.lead_id,
            "agent_user_id": self.agent_user_id,
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