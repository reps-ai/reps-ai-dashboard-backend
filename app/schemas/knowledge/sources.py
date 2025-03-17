from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.schemas.common.knowledge_types import SourceType

class SourceBase(BaseModel):
    name: str
    type: str
    category: str
    description: Optional[str] = None

class SourceCreate(SourceBase):
    url: Optional[str] = None
    file_path: Optional[str] = None

class SourceResponse(SourceBase):
    id: str
    url: Optional[str] = None
    file_path: Optional[str] = None
    entry_count: int
    created_at: str
    updated_at: Optional[str] = None

class SourceDetailResponse(SourceResponse):
    entries: List[str] = []

class PaginationInfo(BaseModel):
    total: int
    page: int
    limit: int
    pages: int

class SourceListResponse(BaseModel):
    data: List[SourceResponse]
    pagination: PaginationInfo 