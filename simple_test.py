# A very simple test to validate Pydantic imports and basic model creation
print("Starting basic Pydantic test...")

try:
    from pydantic import BaseModel, Field, validator
    print("Successfully imported Pydantic")
    
    class SimpleModel(BaseModel):
        name: str = Field(..., description="A name")
        value: int = Field(0, description="A value")
    
    # Try to create a model instance
    instance = SimpleModel(name="Test")
    print(f"Successfully created model: {instance}")
    print("Basic Pydantic functionality works!")
except Exception as e:
    print(f"Error: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()
