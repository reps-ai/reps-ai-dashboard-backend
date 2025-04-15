from enum import Enum
from typing import List, Optional
from pydantic import field_validator, StringConstraints, ConfigDict, BaseModel, Field
from typing_extensions import Annotated

class KnowledgeCategory(str, Enum):
    """Enum for knowledge categories
    
    Used to categorize knowledge entries for organization and retrieval
    """
    GENERAL = "general"
    MEMBERSHIP = "membership"
    PRICING = "pricing"
    FACILITIES = "facilities"
    CLASSES = "classes"
    TRAINERS = "trainers"
    POLICY = "policy"
    OTHER = "other"

class SourceType(str, Enum):
    """Enum for knowledge source types
    
    Defines the type of source a knowledge item originated from
    """
    PDF = "pdf"
    WEBSITE = "website"
    DOC = "doc"
    MANUAL = "manual"
    OTHER = "other"

class ImportStatus(str, Enum):
    """Enum for import job statuses
    
    Tracks the status of knowledge import operations
    """
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    
class CategoryModel(BaseModel):
    """Model for knowledge category statistics
    
    Used to represent category counts in the knowledge base
    """
    category: Annotated[str, StringConstraints(min_length=1)] = Field(
        ...,
        description="Category name (either predefined or custom)",
        examples=["membership"]
    )
    count: int = Field(
        ...,
        ge=0,
        description="Number of knowledge entries in this category",
        examples=[15]
    )
    
    @field_validator('category')
    @classmethod
    def validate_category(cls, v):
        try:
            return KnowledgeCategory(v).value
        except ValueError:
            # Allow custom categories if not in the enum
            if not v or not v.strip():
                raise ValueError("Category cannot be empty")
            return v
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "category": "membership",
            "count": 15
        }
    })

class KnowledgeStatistics(BaseModel):
    """Model for knowledge base statistics
    
    Provides aggregate information about the knowledge base
    """
    total_entries: int = Field(
        ...,
        ge=0,
        description="Total number of knowledge entries",
        examples=[120]
    )
    categories: List[CategoryModel] = Field(
        ...,
        description="Breakdown of entries by category",
    )
    sources: int = Field(
        ...,
        ge=0,
        description="Number of unique knowledge sources",
        examples=[8]
    )
    last_updated: Optional[str] = Field(
        None,
        description="ISO timestamp of the last knowledge base update",
        examples=["2025-03-25T14:30:00Z"]
    )
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "total_entries": 120,
            "categories": [
                {"category": "membership", "count": 45},
                {"category": "facilities", "count": 25},
                {"category": "pricing", "count": 20},
                {"category": "general", "count": 30}
            ],
            "sources": 8,
            "last_updated": "2025-03-25T14:30:00Z"
        }
    })