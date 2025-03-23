from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, validator

class KnowledgeCategory(str, Enum):
    GENERAL = "general"
    MEMBERSHIP = "membership"
    PRICING = "pricing"
    FACILITIES = "facilities"
    CLASSES = "classes"
    TRAINERS = "trainers"
    POLICY = "policy"
    OTHER = "other"

class SourceType(str, Enum):
    PDF = "pdf"
    WEBSITE = "website"
    DOC = "doc"
    MANUAL = "manual"
    OTHER = "other"

class ImportStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    
class CategoryModel(BaseModel):
    category: str = Field(
        ...,
        min_length=1,
        description="Category name",
        example="membership"
    )
    count: int = Field(
        ...,
        ge=0,
        description="Number of knowledge entries in this category",
        example=15
    )
    
    @validator('category')
    def validate_category(cls, v):
        try:
            return KnowledgeCategory(v).value
        except ValueError:
            # Allow custom categories if not in the enum
            return v
    
    class Config:
        schema_extra = {
            "example": {
                "category": "membership",
                "count": 15
            }
        }