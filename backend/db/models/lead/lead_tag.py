"""
Association table for the many-to-many relationship between leads and tags.
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Table
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from ...base import Base

# Association table for many-to-many relationship between leads and tags
lead_tag = Table(
    "lead_tag",
    Base.metadata,
    Column("lead_id", UUID(as_uuid=True), ForeignKey("leads.id"), primary_key=True),
    Column("tag_id", UUID(as_uuid=True), ForeignKey("tags.id"), primary_key=True),
    Column("created_at", DateTime, default=func.now(), nullable=False)
)