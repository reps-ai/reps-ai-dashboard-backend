"""
FollowUpCampaign model for tracking campaigns to follow up with leads.
"""
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text
from uuid import uuid4
from sqlalchemy.dialects.postgresql import UUID, JSONB

from ...base import Base

class FollowUpCampaign(Base):
    """FollowUpCampaign model for tracking campaigns to follow up with leads."""
    
    __tablename__ = "follow_up_campaigns"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    # Remove lead_id column since one campaign can have many leads
    gym_id = Column(UUID(as_uuid=True), ForeignKey("gyms.id"), nullable=False)
    branch_id = Column(UUID(as_uuid=True), ForeignKey("branches.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    frequency = Column(Integer, nullable=False)  # Frequency of follow-ups in days
    gap = Column(Integer, nullable=False)  # Gap between follow-ups in days
    # Update campaign_status with proper default and valid values
    # Valid values: not_started, active, paused, cancelled, completed
    campaign_status = Column(String(50), nullable=False, server_default="not_started")
    created_at = Column(TIMESTAMP(timezone=True),nullable=False,server_default=text('now()'))
    updated_at = Column(TIMESTAMP(timezone=True),nullable=False,server_default=text('now()'),onupdate=text('now()'))
    
    # Add this column to track call counts directly in the campaign table
    call_count = Column(Integer, nullable=False, default=0)
    
    # Add metrics column to store additional campaign metrics
    metrics = Column(JSONB, nullable=True)
    
    def to_dict(self):
        """Convert the model instance to a dictionary."""
        return {
            "id": self.id,
            # Remove lead_id from the dictionary
            "gym_id": self.gym_id,
            "branch_id": self.branch_id,
            "name": self.name,
            "description": self.description,
            "start_date": self.start_date,
            "end_date": self.end_date,
            # Include both period and frequency for backwards compatibility
            "period": self.frequency,
            "frequency": self.frequency,  # Explicitly include frequency field
            "gap": self.gap,
            "campaign_status": self.campaign_status,
            "call_count": self.call_count,
            "metrics": self.metrics if self.metrics else {},
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

# Import dependent models to ensure registration:
from backend.db.models.call.call_log import CallLog
from backend.db.models.lead.lead import Lead
from backend.db.models.call.follow_up_call import FollowUpCall
from backend.db.models.gym.gym import Gym
from backend.db.models.gym.branch import Branch

# Keep these relationship definitions and remove the ones inside the class
FollowUpCampaign.call_logs = relationship("CallLog", back_populates="campaign")
FollowUpCampaign.follow_up_calls = relationship("FollowUpCall", back_populates="campaign")
FollowUpCampaign.gym = relationship("Gym", back_populates="follow_up_campaign")
FollowUpCampaign.branch = relationship("Branch", back_populates="follow_up_campaigns")

# Update relationship to be one-to-many from campaign to leads
FollowUpCampaign.leads = relationship("Lead", foreign_keys="Lead.campaign_id", back_populates="follow_up_campaign")