from pydantic import field_validator, ConfigDict, BaseModel, Field, constr, HttpUrl, AnyHttpUrl, Annotated
from typing import List, Optional, Annotated
from datetime import datetime
from app.schemas.common.knowledge_types import SourceType, ImportStatus

class SourceBase(BaseModel):
    name: Annotated[str, Field(
        min_length=1,
        description="Name of the source",
        examples=["Gym Policies"]
    )]
    type: str = Field(
        ..., 
        description="Type of the source (pdf, website, doc, manual, other)",
        examples=["pdf"]
    )
    category: Annotated[str, Field(
        min_length=1,
        description="Category of the source",
        examples=["gym"]
    )]
    url: Optional[str] = Field(
        None, 
        description="URL of the source, if applicable",
        examples=["https://example.com/gym-policies"]
    )
    description: Optional[str] = Field(
        None, 
        description="Description of the source",
        examples=["Official gym policies and rules"]
    )
    
    @field_validator('type')
    @classmethod
    def validate_type(cls, v):
        try:
            return SourceType(v).value
        except ValueError:
            raise ValueError(f'Type must be one of: {[t.value for t in SourceType]}')
    
    @field_validator('url')
    @classmethod
    def validate_url(cls, v):
        if v is not None:
            if not (v.startswith('http://') or v.startswith('https://')):
                raise ValueError('URL must start with http:// or https://')
            # Additional validation could be done here
        return v
    model_config = ConfigDict(use_enum_values=True, json_schema_extra={
        "example": {
            "name": "Gym Policies",
            "type": "pdf",
            "category": "gym",
            "url": "https://example.com/gym-policies",
            "description": "Official gym policies and rules"
        }
    })

class SourceCreate(SourceBase):
    file_path: Optional[str] = Field(
        None, 
        description="File path of the source, if applicable",
        examples=["/path/to/source.pdf"]
    )
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "name": "Gym Policies",
            "type": "pdf",
            "category": "gym",
            "url": "https://example.com/gym-policies",
            "description": "Official gym policies and rules",
            "file_path": "/path/to/source.pdf"
        }
    })

class SourceResponse(SourceBase):
    id: Annotated[str, Field(
        min_length=1,
        description="Unique identifier for the source",
        examples=["source-123"]
    )]
    file_path: Optional[str] = Field(
        None, 
        description="File path of the source, if applicable",
        examples=["/path/to/source.pdf"]
    )
    created_at: str = Field(
        ..., 
        description="Creation timestamp in ISO format (UTC)",
        examples=["2025-03-15T10:00:00Z"]
    )
    updated_at: Optional[str] = Field(
        None, 
        description="Last update timestamp in ISO format (UTC)",
        examples=["2025-03-20T15:30:00Z"]
    )
    entry_count: int = Field(
        ..., 
        ge=0, 
        description="Number of knowledge entries from this source",
        examples=[15]
    )
    
    @field_validator('created_at')
    @classmethod
    def validate_created_at(cls, v):
        try:
            # Parse the datetime to validate format
            datetime.fromisoformat(v.replace('Z', '+00:00'))
        except ValueError:
            raise ValueError('Timestamp must be a valid ISO datetime format (e.g., 2025-03-15T10:00:00Z)')
        return v
    
    @field_validator('updated_at')
    @classmethod
    def validate_updated_at(cls, v):
        if v is not None:
            try:
                # Parse the datetime to validate format
                datetime.fromisoformat(v.replace('Z', '+00:00'))
            except ValueError:
                raise ValueError('Timestamp must be a valid ISO datetime format (e.g., 2025-03-20T15:30:00Z)')
        return v
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "id": "source-123",
            "name": "Gym Policies",
            "type": "pdf",
            "category": "gym",
            "url": "https://example.com/gym-policies",
            "description": "Official gym policies and rules",
            "file_path": "/path/to/source.pdf",
            "created_at": "2025-03-15T10:00:00Z",
            "updated_at": "2025-03-20T15:30:00Z",
            "entry_count": 15
        }
    })

class SourceDetailResponse(SourceResponse):
    entries: List[str] = Field(
        ..., 
        description="List of entries from the source",
        examples=[["entry1", "entry2"]]
    )
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "id": "source-123",
            "name": "Gym Policies",
            "type": "pdf",
            "category": "gym",
            "url": "https://example.com/gym-policies",
            "description": "Official gym policies and rules",
            "file_path": "/path/to/source.pdf",
            "created_at": "2025-03-15T10:00:00Z",
            "updated_at": "2025-03-20T15:30:00Z",
            "entry_count": 15,
            "entries": [
                "What are the gym hours?",
                "What is the cancellation policy?",
                "How do I book a training session?"
            ]
        }
    })

class PaginationInfo(BaseModel):
    total: int = Field(..., ge=0, description="Total number of sources", examples=[100])
    page: int = Field(..., ge=1, description="Current page number", examples=[1])
    limit: int = Field(..., ge=1, description="Number of sources per page", examples=[10])
    pages: int = Field(..., ge=1, description="Total number of pages", examples=[10])
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "total": 100,
            "page": 1,
            "limit": 10,
            "pages": 10
        }
    })

class SourceListResponse(BaseModel):
    data: List[SourceResponse] = Field(..., description="List of source entries")
    pagination: PaginationInfo = Field(..., description="Pagination information")
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "data": [
                {
                    "id": "source-123",
                    "name": "Gym Policies",
                    "type": "pdf",
                    "category": "gym",
                    "url": "https://example.com/gym-policies",
                    "description": "Official gym policies and rules",
                    "created_at": "2025-03-15T10:00:00Z",
                    "entry_count": 15
                },
                {
                    "id": "source-124",
                    "name": "Membership FAQ",
                    "type": "website",
                    "category": "membership",
                    "url": "https://example.com/membership-faq",
                    "description": "Frequently asked questions about memberships",
                    "created_at": "2025-03-16T10:00:00Z",
                    "entry_count": 20
                }
            ],
            "pagination": {
                "total": 100,
                "page": 1,
                "limit": 10,
                "pages": 10
            }
        }
    })