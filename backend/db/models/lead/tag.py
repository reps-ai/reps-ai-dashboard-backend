"""
Tag model for categorizing leads.
"""
from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from uuid import uuid4

from ..base import Base

class Tag(Base):
    """Tag model for categorizing leads."""
    
    __tablename__ = "tags"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name = Column(String(100), nullable=False)
    color = Column(String(20), nullable=True)  # Hex color code
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    leads = relationship("Lead", secondary="lead_tag", back_populates="tags")
    
    def to_dict(self):
        """Convert the model instance to a dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "color": self.color,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        } 