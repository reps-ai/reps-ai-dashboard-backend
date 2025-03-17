"""
Member model for tracking converted leads who became gym members.
"""
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from uuid import uuid4

from ..base import Base

class Member(Base):
    """Member model for tracking converted leads who became gym members."""
    
    __tablename__ = "members"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    lead_id = Column(String(36), ForeignKey("leads.id"), nullable=False)
    branch_id = Column(String(36), ForeignKey("branches.id"), nullable=False)
    membership_start_date = Column(DateTime, nullable=False)
    membership_type = Column(String(100), nullable=False)
    membership_status = Column(String(50), nullable=False)  # active, inactive, cancelled, etc.
    payment_method = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    lead = relationship("Lead", back_populates="member")
    branch = relationship("Branch", back_populates="members")
    
    def to_dict(self):
        """Convert the model instance to a dictionary."""
        return {
            "id": self.id,
            "lead_id": self.lead_id,
            "branch_id": self.branch_id,
            "membership_start_date": self.membership_start_date,
            "membership_type": self.membership_type,
            "membership_status": self.membership_status,
            "payment_method": self.payment_method,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        } 