"""
GymSettings model for storing gym-specific settings.
"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from uuid import uuid4

from ..base import Base

class GymSettings(Base):
    """GymSettings model for storing gym-specific settings."""
    
    __tablename__ = "gym_settings"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    branch_id = Column(String(36), ForeignKey("branches.id"), nullable=False, unique=True)
    name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=False)
    address = Column(String(255), nullable=False)
    website = Column(String(255), nullable=True)
    email = Column(String(255), nullable=False)
    logo_url = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    branch = relationship("Branch", back_populates="gym_settings")
    
    def to_dict(self):
        """Convert the model instance to a dictionary."""
        return {
            "id": self.id,
            "branch_id": self.branch_id,
            "name": self.name,
            "phone": self.phone,
            "address": self.address,
            "website": self.website,
            "email": self.email,
            "logo_url": self.logo_url,
            "description": self.description,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        } 