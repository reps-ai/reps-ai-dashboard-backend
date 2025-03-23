from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
from app.schemas.common.knowledge_types import SourceType, ImportStatus

class SourceBase(BaseModel):
    name: str = Field(
        ..., 
        min_length=1,
        description="Name of the source",
        example="Gym Policies"
    )
    type: str = Field(
        ..., 
        description="Type of the source",
        example="pdf"
    )
    category: str = Field(
        ..., 
        description="Category of the source",
        example="gym"
    )
    url: Optional[str] = Field(
        None, 
        description="URL of the source, if applicable",
        example="https://example.com/gym-policies"
    )
    description: Optional[str] = Field(
        None, 
        description="Description of the source",
        example="Official gym policies and rules"
    )
    
    @validator('url')
    def validate_url(cls, v):
        if v is not None and not (v.startswith('http://') or v.startswith('https://')):
            raise ValueError('URL must start with http:// or https://')
        return v

class SourceCreate(SourceBase):
    file_path: Optional[str] = Field(
        None, 
        description="File path of the source, if applicable",
        example="/path/to/source.pdf"
    )

class SourceResponse(SourceBase):
    id: str = Field(..., description="Unique identifier for the source")
    url: Optional[str] = Field(
        None, 
        description="URL of the source, if applicable",
        example="https://example.com/gym-policies"
    )
    file_path: Optional[str] = Field(
        None, 
        description="File path of the source, if applicable",
        example="/path/to/source.pdf"
    )
    created_at: str = Field(
        ..., 
        description="Creation timestamp in ISO format",
        example="2025-03-15T10:00:00Z"
    )
    updated_at: Optional[str] = Field(
        None, 
        description="Last update timestamp in ISO format",
        example="2025-03-20T15:30:00Z"
    )
    entry_count: int = Field(
        ..., 
        ge=0, 
        description="Number of knowledge entries from this source",
        example=15
    )
    
    @validator('created_at')
    def validate_created_at(cls, v):
        try:
            # Parse the datetime to validate format
            datetime.fromisoformat(v.replace('Z', '+00:00'))
        except ValueError:
            raise ValueError('Timestamp must be a valid ISO datetime format')
        return v
    
    @validator('updated_at')
    def validate_updated_at(cls, v):
        if v is not None:
            try:
                # Parse the datetime to validate format
                datetime.fromisoformat(v.replace('Z', '+00:00'))
            except ValueError:
                raise ValueError('Timestamp must be a valid ISO datetime format')
        return v

class SourceDetailResponse(SourceResponse):
    entries: List[str] = Field(
        ..., 
        description="List of entries from the source",
        example=["entry1", "entry2"]
    )

class PaginationInfo(BaseModel):
    total: int = Field(..., description="Total number of sources", example=100)
    page: int = Field(..., description="Current page number", example=1)
    limit: int = Field(..., description="Number of sources per page", example=10)
    pages: int = Field(..., description="Total number of pages", example=10)

class SourceListResponse(BaseModel):
    data: List[SourceResponse] = Field(..., description="List of source entries")
    pagination: PaginationInfo = Field(..., description="Pagination information")