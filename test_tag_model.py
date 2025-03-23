from app.schemas.common.lead_types import Tag
import sys

# Simple test script with detailed error reporting
try:
    print("Creating valid Tag model...")
    tag = Tag(id="tag-123", name="VIP", color="#FF5733")
    print(f"Success! Created tag: {tag.dict()}")
    print("Validation passed!")
except Exception as e:
    print(f"Error: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
