from typing import Generic, TypeVar, List, Optional
from pydantic import BaseModel
from pydantic.generics import GenericModel

T = TypeVar('T')

class PaginationMeta(BaseModel):
    page: int
    page_size: int
    total_items: int
    total_pages: int

class PaginatedResponse(GenericModel, Generic[T]):
    data: List[T]
    meta: PaginationMeta

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None