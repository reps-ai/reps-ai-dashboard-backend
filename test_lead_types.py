from app.schemas.common.lead_types import Tag, AssignedStaff, LeadStatus, LeadSource
from pydantic import ValidationError

def test_tag():
    print("Testing Tag model...")
    
    # Valid tag
    try:
        tag = Tag(id="tag-123", name="VIP", color="#FF5733")
        print(f"Valid tag created: {tag}")
    except ValidationError as e:
        print(f"Error creating valid tag: {e}")
        return False
    
    # Invalid color
    try:
        tag = Tag(id="tag-123", name="VIP", color="invalid-color")
        print(f"WARNING: Invalid color accepted: {tag}")
    except ValidationError as e:
        print(f"Good: Invalid color rejected")

    # Empty name
    try:
        tag = Tag(id="tag-123", name="", color="#FF5733")
        print(f"WARNING: Empty name accepted: {tag}")
    except ValidationError as e:
        print(f"Good: Empty name rejected")
        
    # Empty id
    try:
        tag = Tag(id="", name="VIP", color="#FF5733")
        print(f"WARNING: Empty id accepted: {tag}")
    except ValidationError as e:
        print(f"Good: Empty id rejected")

def test_assigned_staff():
    print("\nTesting AssignedStaff model...")
    
    # Valid staff
    try:
        staff = AssignedStaff(id="staff-123", first_name="John", last_name="Doe")
        print(f"Valid staff created: {staff}")
    except ValidationError as e:
        print(f"Error creating valid staff: {e}")
        return False
    
    # Empty id
    try:
        staff = AssignedStaff(id="", first_name="John", last_name="Doe")
        print(f"WARNING: Empty id accepted: {staff}")
    except ValidationError as e:
        print(f"Good: Empty id rejected")

    # Empty first_name
    try:
        staff = AssignedStaff(id="staff-123", first_name="", last_name="Doe")
        print(f"WARNING: Empty first_name accepted: {staff}")
    except ValidationError as e:
        print(f"Good: Empty first_name rejected")
        
    # Empty last_name
    try:
        staff = AssignedStaff(id="staff-123", first_name="John", last_name="")
        print(f"WARNING: Empty last_name accepted: {staff}")
    except ValidationError as e:
        print(f"Good: Empty last_name rejected")

def test_enums():
    print("\nTesting enum values...")
    print(f"LeadStatus values: {[s.value for s in LeadStatus]}")
    print(f"LeadSource values: {[s.value for s in LeadSource]}")

if __name__ == "__main__":
    test_tag()
    test_assigned_staff()
    test_enums()
