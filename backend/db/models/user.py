"""
User model representing system users with different roles.
"""
from sqlalchemy import Column, String, DateTime, Boolean, Table, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from uuid import uuid4

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
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    username = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    role = Column(String(50), nullable=False)  # admin, manager, agent, etc.
    phone = Column(String(20), nullable=True)
    profile_picture = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    assigned_leads = relationship("Lead", foreign_keys="Lead.assigned_to_user_id", back_populates="assigned_to")
    call_logs = relationship("CallLog", foreign_keys="CallLog.agent_user_id", back_populates="agent")
    appointments_as_employee = relationship("Appointment", foreign_keys="Appointment.employee_user_id", back_populates="employee")
    appointments_created = relationship("Appointment", foreign_keys="Appointment.created_by_user_id", back_populates="created_by")
    follow_up_calls = relationship("FollowUpCall", foreign_keys="FollowUpCall.agent_user_id", back_populates="agent")
    branches = relationship("Branch", secondary=user_branch, back_populates="users")
    
    def to_dict(self):
        """Convert the model instance to a dictionary."""
        return {
            "id": self.id,
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