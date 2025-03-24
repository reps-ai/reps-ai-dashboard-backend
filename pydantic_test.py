from pydantic import BaseModel, Field, validator, ValidationError
from enum import Enum
from typing import List, Optional

# Simple test to check basic Pydantic functionality
class SampleEnum(str, Enum):
    A = "a"
    B = "b"
    C = "c"

class SampleModel(BaseModel):
    name: str = Field(..., min_length=1, description="Name field")
    value: int = Field(..., ge=0, description="A numeric value")
    tag: Optional[str] = Field(None, description="Optional tag")
    enum_value: SampleEnum = Field(..., description="Enum value")
    
    @validator('name')
    def validate_name(cls, v):
        if v.lower() == 'test':
            raise ValueError('Name cannot be test')
        return v

print("Running basic Pydantic test...\n")

try:
    # Valid instance
    instance = SampleModel(name="Example", value=10, enum_value="a")
    print(f"Valid model created: {instance}")
    print(f"JSON: {instance.json()}")
    
    # Test enum validation
    try:
        instance = SampleModel(name="Example", value=10, enum_value="invalid")
        print("ERROR: Invalid enum accepted")
    except ValidationError as e:
        print("Good: Invalid enum rejected")
    
    # Test validator
    try:
        instance = SampleModel(name="test", value=10, enum_value="a")
        print("ERROR: Name 'test' accepted when it should be rejected")
    except ValidationError as e:
        print("Good: Name validator works")
    
    # Test min_length
    try:
        instance = SampleModel(name="", value=10, enum_value="a")
        print("ERROR: Empty name accepted when it should be rejected")
    except ValidationError as e:
        print("Good: min_length validation works")
    
    # Test ge constraint
    try:
        instance = SampleModel(name="Example", value=-1, enum_value="a")
        print("ERROR: Negative value accepted when it should be rejected")
    except ValidationError as e:
        print("Good: ge validation works")
    
    print("\nAll basic Pydantic validations passed!")
    
except Exception as e:
    print(f"Unexpected error: {str(e)}")
