"""
Lead model representing potential gym members.
"""
from sqlalchemy import Column, String, Integer, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text
from uuid import uuid4

from ..base import Base


class Lead(Base):
    """Lead model representing potential gym members."""
    
    __tablename__ = "leads"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    branch_id = Column(String(36), ForeignKey("branches.id"), nullable=False)
    gym_id = Column(String(36), ForeignKey("gyms.id"), nullable=False)
    assigned_to_user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)
    email = Column(String(255), nullable=True)
    lead_status = Column(String(50), nullable=False, default="new")  # new, contacted, qualified, converted, closed
    notes = Column(Text, nullable=True)
    interest = Column(String(255), nullable=True)
    interest_location = Column(String(255), nullable=True)
    last_conversation_summary = Column(Text, nullable=True)
    last_called = Column(DateTime, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True),nullable=False,server_default=text('now()'))
    updated_at = Column(TIMESTAMP(timezone=True),nullable=False,server_default=text('now()'),onupdate=text('now()'))
    score = Column(Integer, nullable=True)
    source = Column(String(100), nullable=True)
    next_appointment_date = Column(DateTime, nullable=True)
    custom_fields = Column(Text, nullable=True)
    fitness_goals = Column(Text, nullable=True)
    budget_range = Column(String(100), nullable=True)
    timeframe = Column(String(100), nullable=True)
    preferred_contact_method = Column(String(50), nullable=True)
    preferred_contact_time = Column(Text, nullable=True)
    urgency = Column(String(50), nullable=True)
    qualification_score = Column(Integer, nullable=True)
    qualification_notes = Column(String(255), nullable=True)
    fitness_level = Column(String(50), nullable=True)
    previous_gym_experience = Column(Boolean, nullable=True)
    specific_health_goals = Column(Text, nullable=True)
    preferred_training_type = Column(Text, nullable=True)
    availability = Column(Text, nullable=True)
    medical_conditions = Column(Text, nullable=True)
    
    def to_dict(self):
        """Convert the model instance to a dictionary."""
        return {
            "id": self.id,
            "branch_id": self.branch_id,
            "gym_id": self.gym_id,
            "assigned_to_user_id": self.assigned_to_user_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "phone": self.phone,
            "email": self.email,
            "lead_status": self.lead_status,
            "notes": self.notes,
            "interest": self.interest,
            "interest_location": self.interest_location,
            "last_conversation_summary": self.last_conversation_summary,
            "last_called": self.last_called,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "score": self.score,
            "source": self.source,
            "next_appointment_date": self.next_appointment_date,
            "custom_fields": self.custom_fields,
            "fitness_goals": self.fitness_goals,
            "budget_range": self.budget_range,
            "timeframe": self.timeframe,
            "preferred_contact_method": self.preferred_contact_method,
            "preferred_contact_time": self.preferred_contact_time,
            "urgency": self.urgency,
            "qualification_score": self.qualification_score,
            "qualification_notes": self.qualification_notes,
            "fitness_level": self.fitness_level,
            "previous_gym_experience": self.previous_gym_experience,
            "specific_health_goals": self.specific_health_goals,
            "preferred_training_type": self.preferred_training_type,
            "availability": self.availability,
            "medical_conditions": self.medical_conditions
        }

# Import dependent models to ensure registration
from backend.db.models.gym.branch import Branch
from backend.db.models.gym.gym import Gym
from backend.db.models.user import User
from backend.db.models.call.call_log import CallLog
from backend.db.models.appointment import Appointment
from backend.db.models.member import Member
from backend.db.models.lead.tag import Tag
from backend.db.models.call.follow_up_call import FollowUpCall
from backend.db.models.campaign.follow_up_campaign import FollowUpCampaign

# Define relationships AFTER the class is defined:
Lead.branch = relationship("Branch", back_populates="leads")
Lead.gym = relationship("Gym", back_populates="leads")
Lead.assigned_to = relationship("User", foreign_keys=[Lead.assigned_to_user_id], back_populates="assigned_leads")
Lead.call_logs = relationship("CallLog", back_populates="lead")
Lead.appointments = relationship("Appointment", back_populates="lead")
Lead.member = relationship("Member", back_populates="lead", uselist=False)
Lead.tags = relationship("Tag", secondary="lead_tag", back_populates="leads")
Lead.follow_up_calls = relationship("FollowUpCall", back_populates="lead")
Lead.follow_up_campaigns = relationship("FollowUpCampaign", back_populates="lead")