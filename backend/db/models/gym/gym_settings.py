"""
GymSettings model for storing gym-specific settings.
"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text
from uuid import uuid4

from ..base import Base

class GymSettings(Base):
    """GymSettings model for storing gym-specific settings."""
    
    __tablename__ = "gym_settings"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    branch_id = Column(String(36), ForeignKey("branches.id"), nullable=False, unique=True)
    gym_id = Column(String(36), ForeignKey("gyms.id"), nullable=False)
    name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=False)
    address = Column(String(255), nullable=False)
    website = Column(String(255), nullable=True)
    email = Column(String(255), nullable=False)
    logo_url = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True),nullable=False,server_default=text('now()'))
    updated_at = Column(TIMESTAMP(timezone=True),nullable=False,server_default=text('now()'),onupdate=text('now()'))
    
    # Relationships
    branch = relationship("Branch", back_populates="gym_settings")
    gym_id = relationship("Gym", back_populates="gym_settings")
    
    def to_dict(self):
        """Convert the model instance to a dictionary."""
        return {
            "id": self.id,
            "branch_id": self.branch_id,
            "gym_id": self.gym_id,
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