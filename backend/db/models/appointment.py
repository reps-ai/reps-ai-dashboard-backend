"""
Appointment model for tracking scheduled appointments with leads.
"""
from sqlalchemy import Column, String, Integer, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship
from uuid import uuid4
from sqlalchemy.dialects.postgresql import UUID

from ..base import Base

class Appointment(Base):
    """Appointment model for tracking scheduled appointments with leads."""
    
    __tablename__ = "appointments"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    gym_id = Column(UUID(as_uuid=True), ForeignKey("gyms.id"), nullable=False)
    lead_id = Column(String(36), ForeignKey("leads.id"), nullable=False)
    branch_id = Column(String(36), ForeignKey("branches.id"), nullable=False)
    employee_user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    appointment_type = Column(String(100), nullable=False)  # tour, consultation, training, etc.
    appointment_date = Column(DateTime, nullable=False)
    duration = Column(Integer, nullable=True)  # in minutes
    appointment_status = Column(String(50), nullable=False)  # scheduled, completed, cancelled, no_show
    notes = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True),nullable=False,server_default=text('now()'))
    updated_at = Column(TIMESTAMP(timezone=True),nullable=False,server_default=text('now()'),onupdate=text('now()'))
    created_by_user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    reminder_sent = Column(Boolean, default=False, nullable=False)
    employee_name = Column(String(255), nullable=True)  # In case employee is not a system user
    
    # Relationships
    gym = relationship("Gym", back_populates="appointments")
    lead = relationship("Lead", back_populates="appointments")
    branch = relationship("Branch", back_populates="appointments")
    employee = relationship("User", foreign_keys=[employee_user_id], back_populates="appointments_as_employee")
    created_by = relationship("User", foreign_keys=[created_by_user_id], back_populates="appointments_created")
    
    def to_dict(self):
        """Convert the model instance to a dictionary."""
        return {
            "id": self.id,
            "gym_id": self.gym_id,
            "lead_id": self.lead_id,
            "branch_id": self.branch_id,
            "employee_user_id": self.employee_user_id,
            "appointment_type": self.appointment_type,
            "appointment_date": self.appointment_date,
            "duration": self.duration,
            "appointment_status": self.appointment_status,
            "notes": self.notes,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "created_by_user_id": self.created_by_user_id,
            "reminder_sent": self.reminder_sent,
            "employee_name": self.employee_name
        } 