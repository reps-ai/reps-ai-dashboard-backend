from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator
from app.schemas.knowledge.base import KnowledgeBase
from app.schemas.common.knowledge_types import ImportStatus

class SourceInfo(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    type: Optional[str] = None

class KnowledgeResponse(KnowledgeBase):
    id: str = Field(..., description="Unique identifier for the knowledge entry")
    created_at: str = Field(
        ..., 
        description="Creation timestamp in ISO format",
        example="2025-03-15T10:00:00Z"
    )
    source: Optional[SourceInfo] = Field(
        None, 
        description="Source information, if applicable"
    )
    
    @validator('created_at')
    def validate_timestamps(cls, v):
        try:
            # Parse the datetime to validate format
            datetime.fromisoformat(v.replace('Z', '+00:00'))
        except ValueError:
            raise ValueError('Timestamp must be a valid ISO datetime format')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "id": "kb-123",
                "question": "What are the gym hours?",
                "answer": "Our gym is open from 5am to 11pm Monday through Friday, and 7am to 9pm on weekends.",
                "category": "general",
                "priority": 5,
                "created_at": "2025-03-15T10:00:00Z"
            }
        }

class KnowledgeDetailResponse(KnowledgeResponse):
    updated_at: str = Field(
        ..., 
        description="Last update timestamp in ISO format",
        example="2025-03-20T15:30:00Z"
    )
    
    @validator('updated_at')
    def validate_updated_at(cls, v):
        try:
            # Parse the datetime to validate format
            datetime.fromisoformat(v.replace('Z', '+00:00'))
        except ValueError:
            raise ValueError('Timestamp must be a valid ISO datetime format')
        return v

class PaginationInfo(BaseModel):
    total: int = Field(..., ge=0, description="Total number of knowledge entries available")
    page: int = Field(..., ge=1, description="Current page number")
    limit: int = Field(..., ge=1, description="Number of entries per page")
    pages: int = Field(..., ge=1, description="Total number of pages available")

class KnowledgeListResponse(BaseModel):
    data: List[KnowledgeResponse] = Field(..., description="List of knowledge entries")
    pagination: PaginationInfo = Field(..., description="Pagination information")

class KnowledgeImportResponse(BaseModel):
    job_id: str = Field(..., description="Unique identifier for the import job")
    status: str = Field(..., description="Status of the import job")
    source_id: Optional[str] = Field(None, description="Source identifier, if applicable")

class DeleteResponse(BaseModel):
    success: bool = Field(..., description="Whether the deletion was successful")