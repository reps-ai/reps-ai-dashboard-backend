"""
FollowUpCampaign model for tracking campaigns to follow up with leads.
"""
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from uuid import uuid4

from ...base import Base

class FollowUpCampaign(Base):
    """FollowUpCampaign model for tracking campaigns to follow up with leads."""
    
    __tablename__ = "follow_up_campaigns"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    lead_id = Column(String(36), ForeignKey("leads.id"), nullable=False)
    branch_id = Column(String(36), ForeignKey("branches.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    frequency = Column(Integer, nullable=False)  # Frequency of follow-ups in days
    gap = Column(Integer, nullable=False)  # Gap between follow-ups in days
    campaign_status = Column(String(50), nullable=False)  # active, completed, paused, cancelled
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    lead = relationship("Lead", back_populates="follow_up_campaigns")
    branch = relationship("Branch", back_populates="follow_up_campaigns")
    follow_up_calls = relationship("FollowUpCall", back_populates="campaign")
    call_logs = relationship("CallLog", back_populates="campaign")
    
    def to_dict(self):
        """Convert the model instance to a dictionary."""
        return {
            "id": self.id,
            "lead_id": self.lead_id,
            "branch_id": self.branch_id,
            "name": self.name,
            "description": self.description,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "period": self.period,
            "campaign_status": self.campaign_status,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        } 