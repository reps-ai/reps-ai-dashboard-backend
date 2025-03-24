from app.schemas.common.lead_types import Tag
from pydantic import ValidationError

print("Starting minimal Tag model test...")

try:
    # Create a valid Tag
    tag = Tag(id="tag-123", name="VIP", color="#FF5733")
    print(f"✓ Valid tag created: {tag}\n")
    
    # Test min_length validation on name
    try:
        tag = Tag(id="tag-123", name="", color="#FF5733")
        print(f"✗ Empty name accepted when it should be rejected\n")
    except ValidationError as e:
        print(f"✓ Empty name correctly rejected: {e}\n")
    
    # Test color validation
    try:
        tag = Tag(id="tag-123", name="VIP", color="invalid-color")
        print(f"✗ Invalid color accepted when it should be rejected\n")
    except ValidationError as e:
        print(f"✓ Invalid color correctly rejected: {e}\n")
        
    print("Tag model test completed successfully!")
    
except Exception as e:
    print(f"Error during testing: {str(e)}")
