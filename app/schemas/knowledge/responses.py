from pydantic import BaseModel
from typing import List, Optional
from app.schemas.knowledge.base import KnowledgeBase
from app.schemas.common.knowledge_types import ImportStatus

class SourceInfo(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    type: Optional[str] = None

class KnowledgeResponse(KnowledgeBase):
    id: str
    created_at: str
    source: Optional[SourceInfo] = None

class KnowledgeDetailResponse(KnowledgeResponse):
    updated_at: str

class PaginationInfo(BaseModel):
    total: int
    page: int
    limit: int
    pages: int

class KnowledgeListResponse(BaseModel):
    data: List[KnowledgeResponse]
    pagination: PaginationInfo

class KnowledgeImportResponse(BaseModel):
    job_id: str
    status: str
    source_id: Optional[str] = None

class DeleteResponse(BaseModel):
    success: bool 