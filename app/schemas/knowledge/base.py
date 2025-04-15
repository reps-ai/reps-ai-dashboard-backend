from pydantic import field_validator, ConfigDict, BaseModel, Field, validator
from typing import Optional, List
from app.schemas.common.knowledge_types import KnowledgeCategory

class KnowledgeBase(BaseModel):
    question: str = Field(
        ..., 
        min_length=5,
        description="Question for the knowledge base entry",
        examples=["What are the gym membership options?"]
    )
    answer: str = Field(
        ..., 
        min_length=10,
        description="Answer to the knowledge base question",
        examples=["We offer three membership tiers: Basic ($29/month), Premium ($49/month), and Elite ($79/month)."]
    )
    category: str = Field(
        ..., 
        description="Category of the knowledge entry",
        examples=["membership"]
    )
    priority: int = Field(
        default=0, 
        ge=0, 
        le=10, 
        description="Priority level of this knowledge (0-10, higher is more important)"
    )
    source_id: Optional[str] = Field(
        None, 
        description="ID of the source document if applicable"
    )
    
    @field_validator('category')
    @classmethod
    def validate_category(cls, v):
        try:
            return KnowledgeCategory(v).value
        except ValueError:
            raise ValueError(f'Category must be one of: {[c.value for c in KnowledgeCategory]}')
    model_config = ConfigDict(use_enum_values=True, json_schema_extra={
        "example": {
            "question": "What are the gym hours?",
            "answer": "Our gym is open from 5am to 11pm Monday through Friday, and 7am to 9pm on weekends.",
            "category": "general",
            "priority": 5
        }
    })

class KnowledgeCreate(KnowledgeBase):
    pass

class KnowledgeUpdate(BaseModel):
    question: Optional[str] = Field(
        None, 
        min_length=5,
        description="Question for the knowledge base entry"
    )
    answer: Optional[str] = Field(
        None, 
        min_length=10,
        description="Answer to the knowledge base question"
    )
    category: Optional[str] = Field(
        None, 
        description="Category of the knowledge entry"
    )
    priority: Optional[int] = Field(
        None, 
        ge=0, 
        le=10, 
        description="Priority level of this knowledge (0-10, higher is more important)"
    )
    source_id: Optional[str] = Field(
        None, 
        description="ID of the source document if applicable"
    )
    
    # Inherit validators from KnowledgeBase
    _validate_category = validator('category', allow_reuse=True)(KnowledgeBase.validate_category)
    model_config = ConfigDict(use_enum_values=True)

class KnowledgeImport(BaseModel):
    url: str = Field(
        ..., 
        description="URL of the source to import knowledge from",
        examples=["https://example.com/gym-policies"]
    )
    category: str = Field(
        ..., 
        description="Category to assign to imported knowledge entries",
        examples=["policies"]
    )
    name: Optional[str] = Field(
        None, 
        description="Custom name for the imported source"
    )
    description: Optional[str] = Field(
        None, 
        description="Description of the imported knowledge source"
    )
    
    @field_validator('category')
    @classmethod
    def validate_category(cls, v):
        try:
            return KnowledgeCategory(v).value
        except ValueError:
            raise ValueError(f'Category must be one of: {[c.value for c in KnowledgeCategory]}')
    
    @field_validator('url')
    @classmethod
    def validate_url(cls, v):
        # Basic URL validation
        if not (v.startswith('http://') or v.startswith('https://')):
            raise ValueError('URL must start with http:// or https://')
        return v
    model_config = ConfigDict(use_enum_values=True)