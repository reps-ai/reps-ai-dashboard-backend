"""
KnowledgeBase model for storing FAQs and knowledge base items.
"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship
from uuid import uuid4

from ...base import Base

class KnowledgeBase(Base):
    """KnowledgeBase model for storing FAQs and knowledge base items."""
    
    __tablename__ = "knowledge_base"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    branch_id = Column(String(36), ForeignKey("branches.id"), nullable=False)
    gym_id = Column(String(36), ForeignKey("gyms.id"), nullable=False)
    pdf_url = Column(String(255), nullable=True)
    question = Column(Text, nullable=True)
    answer = Column(Text, nullable=True)
    tags = Column(Text, nullable=True)  # JSON array of tags
    created_at = Column(TIMESTAMP(timezone=True),nullable=False,server_default=text('now()'))
    updated_at = Column(TIMESTAMP(timezone=True),nullable=False,server_default=text('now()'),onupdate=text('now()'))
    
    # Relationships
    branch = relationship("Branch", back_populates="knowledge_base")
    gym = relationship("Gym", back_populates="knowledge_base")
    
    def to_dict(self):
        """Convert the model instance to a dictionary."""
        return {
            "id": self.id,
            "branch_id": self.branch_id,
            "gym_id": self.gym_id,
            "pdf_url": self.pdf_url,
            "question": self.question,
            "answer": self.answer,
            "tags": self.tags,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        } 