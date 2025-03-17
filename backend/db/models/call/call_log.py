"""
CallLog model for tracking calls made to leads.
"""
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from uuid import uuid4

from ..base import Base

class CallLog(Base):
    """CallLog model for tracking calls made to leads."""
    
    __tablename__ = "call_logs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    lead_id = Column(String(36), ForeignKey("leads.id"), nullable=False)
    agent_user_id = Column(String(36), ForeignKey("users.id"), nullable=True)  # Null if AI call
    duration = Column(Integer, nullable=True)  # in seconds
    call_type = Column(String(50), nullable=False)  # outbound, inbound, ai, etc.
    human_notes = Column(Text, nullable=True)
    outcome = Column(String(50), nullable=True)  # scheduled, not_interested, callback, etc.
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    call_status = Column(String(50), nullable=False)  # scheduled, in_progress, completed, failed, etc.
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    recording_url = Column(String(255), nullable=True)
    transcript = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    sentiment = Column(String(50), nullable=True)  # positive, negative, neutral
    campaign_id = Column(String(36), ForeignKey("follow_up_campaigns.id"), nullable=True)
    
    # Relationships
    lead = relationship("Lead", back_populates="call_logs")
    agent = relationship("User", foreign_keys=[agent_user_id], back_populates="call_logs")
    campaign = relationship("FollowUpCampaign", back_populates="call_logs")
    
    def to_dict(self):
        """Convert the model instance to a dictionary."""
        return {
            "id": self.id,
            "lead_id": self.lead_id,
            "agent_user_id": self.agent_user_id,
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