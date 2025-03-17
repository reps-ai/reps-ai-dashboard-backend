"""
Association table for the many-to-many relationship between leads and tags.
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Table
from sqlalchemy.sql import func

from ...base import Base

# Association table for many-to-many relationship between leads and tags
lead_tag = Table(
    "lead_tag",
    Base.metadata,
    Column("lead_id", String(36), ForeignKey("leads.id"), primary_key=True),
    Column("tag_id", String(36), ForeignKey("tags.id"), primary_key=True),
    Column("created_at", DateTime, default=func.now(), nullable=False)
) 