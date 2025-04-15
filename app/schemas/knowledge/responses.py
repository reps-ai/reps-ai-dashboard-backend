from typing import List, Optional
from datetime import datetime
from pydantic import field_validator, StringConstraints, ConfigDict, BaseModel, Field, HttpUrl
from app.schemas.knowledge.base import KnowledgeBase
from app.schemas.common.knowledge_types import ImportStatus, SourceType
from typing_extensions import Annotated

class SourceInfo(BaseModel):
    id: Optional[Annotated[str, StringConstraints(min_length=1)]] = Field(
        None, 
        description="Unique identifier for the knowledge source",
        examples=["source-123"]
    )
    name: Optional[Annotated[str, StringConstraints(min_length=1)]] = Field(
        None, 
        description="Name of the knowledge source",
        examples=["Employee Handbook"]
    )
    type: Optional[str] = Field(
        None, 
        description="Type of source (pdf, website, doc, manual, other)",
        examples=["pdf"]
    )
    
    @field_validator('type')
    @classmethod
    def validate_type(cls, v):
        if v is not None:
            try:
                return SourceType(v).value
            except ValueError:
                raise ValueError(f'Type must be one of: {[t.value for t in SourceType]}')
        return v
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "id": "source-123",
            "name": "Employee Handbook",
            "type": "pdf"
        }
    })

class KnowledgeResponse(KnowledgeBase):
    id: Annotated[str, StringConstraints(min_length=1)] = Field(
        ..., 
        description="Unique identifier for the knowledge entry",
        examples=["kb-123"]
    )
    created_at: str = Field(
        ..., 
        description="Creation timestamp in ISO format (UTC)",
        examples=["2025-03-15T10:00:00Z"]
    )
    source: Optional[SourceInfo] = Field(
        None, 
        description="Source information, if applicable"
    )
    
    @field_validator('created_at')
    @classmethod
    def validate_timestamps(cls, v):
        try:
            # Parse the datetime to validate format
            datetime.fromisoformat(v.replace('Z', '+00:00'))
        except ValueError:
            raise ValueError('Timestamp must be a valid ISO datetime format (e.g., 2025-03-15T10:00:00Z)')
        return v
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "id": "kb-123",
            "question": "What are the gym hours?",
            "answer": "Our gym is open from 5am to 11pm Monday through Friday, and 7am to 9pm on weekends.",
            "category": "general",
            "priority": 5,
            "created_at": "2025-03-15T10:00:00Z",
            "source": {
                "id": "source-123",
                "name": "Employee Handbook",
                "type": "pdf"
            }
        }
    })

class KnowledgeDetailResponse(KnowledgeResponse):
    updated_at: str = Field(
        ..., 
        description="Last update timestamp in ISO format (UTC)",
        examples=["2025-03-20T15:30:00Z"]
    )
    
    @field_validator('updated_at')
    @classmethod
    def validate_updated_at(cls, v):
        try:
            # Parse the datetime to validate format
            datetime.fromisoformat(v.replace('Z', '+00:00'))
        except ValueError:
            raise ValueError('Timestamp must be a valid ISO datetime format (e.g., 2025-03-20T15:30:00Z)')
        return v
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "id": "kb-123",
            "question": "What are the gym hours?",
            "answer": "Our gym is open from 5am to 11pm Monday through Friday, and 7am to 9pm on weekends.",
            "category": "general",
            "priority": 5,
            "created_at": "2025-03-15T10:00:00Z",
            "updated_at": "2025-03-20T15:30:00Z",
            "source": {
                "id": "source-123",
                "name": "Employee Handbook",
                "type": "pdf"
            }
        }
    })

class PaginationInfo(BaseModel):
    total: int = Field(..., ge=0, description="Total number of knowledge entries available")
    page: int = Field(..., ge=1, description="Current page number")
    limit: int = Field(..., ge=1, description="Number of entries per page")
    pages: int = Field(..., ge=1, description="Total number of pages available")
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "total": 100,
            "page": 1,
            "limit": 20,
            "pages": 5
        }
    })

class KnowledgeListResponse(BaseModel):
    data: List[KnowledgeResponse] = Field(..., description="List of knowledge entries")
    pagination: PaginationInfo = Field(..., description="Pagination information")
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "data": [
                {
                    "id": "kb-123",
                    "question": "What are the gym hours?",
                    "answer": "Our gym is open from 5am to 11pm Monday through Friday, and 7am to 9pm on weekends.",
                    "category": "general",
                    "priority": 5,
                    "created_at": "2025-03-15T10:00:00Z"
                },
                {
                    "id": "kb-124",
                    "question": "What is the cancellation policy?",
                    "answer": "Members can cancel their membership with 30 days notice.",
                    "category": "membership",
                    "priority": 4,
                    "created_at": "2025-03-16T10:00:00Z"
                }
            ],
            "pagination": {
                "total": 100,
                "page": 1,
                "limit": 20,
                "pages": 5
            }
        }
    })

class KnowledgeImportResponse(BaseModel):
    job_id: Annotated[str, StringConstraints(min_length=1)] = Field(
        ..., 
        description="Unique identifier for the import job",
        examples=["job-123"]
    )
    status: str = Field(
        ..., 
        description="Status of the import job (pending, processing, completed, failed)",
        examples=["processing"]
    )
    source_id: Optional[Annotated[str, StringConstraints(min_length=1)]] = Field(
        None, 
        description="Source identifier, if applicable",
        examples=["source-123"]
    )
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        try:
            return ImportStatus(v).value
        except ValueError:
            raise ValueError(f'Status must be one of: {[s.value for s in ImportStatus]}')
        return v
    model_config = ConfigDict(use_enum_values=True, json_schema_extra={
        "example": {
            "job_id": "job-123",
            "status": "processing",
            "source_id": "source-123"
        }
    })

class DeleteResponse(BaseModel):
    success: bool = Field(
        ..., 
        description="Whether the deletion was successful",
        examples=[True]
    )
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "success": True
        }
    })