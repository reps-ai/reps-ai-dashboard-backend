"""
User model representing system users with different roles.
"""
from sqlalchemy import Column, String, DateTime, Boolean, Table, ForeignKey
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship
from uuid import uuid4
from sqlalchemy.dialects.postgresql import UUID

from ..base import Base

# Association table for many-to-many relationship between users and branches
user_branch = Table(
    "user_branch",
    Base.metadata,
    Column("user_id", String(36), ForeignKey("users.id"), primary_key=True),
    Column("branch_id", String(36), ForeignKey("branches.id"), primary_key=True)
)

class User(Base):
    """User model representing system users with different roles."""
    
    __tablename__ = "users"
    
    # Changed from String to UUID type with direct uuid4 function
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    gym_id = Column(UUID(as_uuid=True), ForeignKey("gyms.id"), nullable=False)
    branch_id = Column(UUID(as_uuid=True), ForeignKey("branches.id"), nullable=False)
    username = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    role = Column(String(50), nullable=False)  # admin, manager, agent, etc.
    phone = Column(String(20), nullable=True)
    profile_picture = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),nullable=False,server_default=text('now()'))
    updated_at = Column(TIMESTAMP(timezone=True),nullable=False,server_default=text('now()'),onupdate=text('now()'))
    
    def to_dict(self):
        """Convert the model instance to a dictionary."""
        return {
            "id": self.id,
            "gym_id": self.gym_id,
            "branch_id": self.branch_id,
            "username": self.username,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "role": self.role,
            "phone": self.phone,
            "profile_picture": self.profile_picture,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

from backend.db.models.gym.gym import Gym
from backend.db.models.gym.branch import Branch
from backend.db.models.lead.lead import Lead
from backend.db.models.call.call_log import CallLog
from backend.db.models.appointment import Appointment
from backend.db.models.call.follow_up_call import FollowUpCall

User.gym = relationship("Gym", back_populates="users")
User.branch = relationship("Branch", back_populates="users")
User.assigned_leads = relationship("Lead", foreign_keys="Lead.assigned_to_user_id", back_populates="assigned_to")
User.appointments_as_employee = relationship("Appointment", foreign_keys="Appointment.employee_user_id", back_populates="employee")
User.appointments_created = relationship("Appointment", foreign_keys="Appointment.created_by_user_id", back_populates="created_by")
User.branches = relationship("Branch", secondary=user_branch, back_populates="users")