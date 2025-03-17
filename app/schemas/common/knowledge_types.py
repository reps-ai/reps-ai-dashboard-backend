from enum import Enum
from pydantic import BaseModel
from typing import Optional

class KnowledgeCategory(str, Enum):
    GENERAL = "general"
    MEMBERSHIP = "membership"
    CLASSES = "classes"
    FACILITIES = "facilities"
    PRICING = "pricing"
    POLICIES = "policies"
    OTHER = "other"

class ImportStatus(str, Enum):
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class SourceType(str, Enum):
    URL = "url"
    FILE = "file"
    MANUAL = "manual" 