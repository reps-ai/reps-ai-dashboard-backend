from pydantic import BaseModel
from typing import Optional, List
from app.schemas.common.knowledge_types import KnowledgeCategory

class KnowledgeBase(BaseModel):
    question: str
    answer: str
    category: str
    priority: int = 0
    source_id: Optional[str] = None

class KnowledgeCreate(KnowledgeBase):
    pass

class KnowledgeUpdate(KnowledgeBase):
    pass

class KnowledgeImport(BaseModel):
    url: str
    category: str
    name: Optional[str] = None
    description: Optional[str] = None 