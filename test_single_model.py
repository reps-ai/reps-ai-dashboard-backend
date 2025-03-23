import sys
import traceback
from datetime import datetime
from pydantic import ValidationError

# Set the model to test via command-line argument
# Example: python test_single_model.py Tag
def test_model(model_name):
    print(f"\n=== Testing {model_name} Model ===\n")
    
    try:
        # Import the model based on the name provided
        if model_name == "Tag":
            from app.schemas.common.lead_types import Tag as ModelClass
            valid_data = {"id": "tag-123", "name": "VIP", "color": "#FF5733"}
            invalid_data_samples = [
                {"id": "tag-123", "name": "VIP", "color": "invalid-color"},  # Invalid color format
                {"id": "tag-123", "name": "", "color": "#FF5733"},           # Empty name
                {"id": "", "name": "VIP", "color": "#FF5733"}               # Empty id
            ]
            
        elif model_name == "AssignedStaff":
            from app.schemas.common.lead_types import AssignedStaff as ModelClass
            valid_data = {"id": "staff-123", "first_name": "John", "last_name": "Doe"}
            invalid_data_samples = [
                {"id": "", "first_name": "John", "last_name": "Doe"},         # Empty id
                {"id": "staff-123", "first_name": "", "last_name": "Doe"},     # Empty first_name
                {"id": "staff-123", "first_name": "John", "last_name": ""}     # Empty last_name
            ]
            
        elif model_name == "TranscriptEntry":
            from app.schemas.common.call_types import TranscriptEntry as ModelClass
            valid_data = {"speaker": "agent", "text": "How can I help you?", "timestamp": 10.5}
            invalid_data_samples = [
                {"speaker": "invalid", "text": "How can I help you?", "timestamp": 10.5},  # Invalid speaker
                {"speaker": "agent", "text": "", "timestamp": 10.5},                     # Empty text
                {"speaker": "agent", "text": "How can I help you?", "timestamp": -1.0}    # Negative timestamp
            ]
            
        elif model_name == "CategoryModel":
            from app.schemas.common.knowledge_types import CategoryModel as ModelClass
            valid_data = {"category": "membership", "count": 15}
            invalid_data_samples = [
                {"category": "", "count": 15},      # Empty category
                {"category": "membership", "count": -1}  # Negative count
            ]
            
        elif model_name == "TimeSlot":
            from app.schemas.common.appointment_types import TimeSlot as ModelClass
            valid_data = {
                "start_time": "2025-03-25T14:00:00Z", 
                "end_time": "2025-03-25T15:00:00Z", 
                "available": True
            }
            invalid_data_samples = [
                {"start_time": "invalid-time", "end_time": "2025-03-25T15:00:00Z", "available": True}, # Invalid start_time
                {"start_time": "2025-03-25T14:00:00Z", "end_time": "invalid-time", "available": True}  # Invalid end_time
            ]
        else:
            print(f"Error: Model '{model_name}' not configured for testing")
            return
        
        # Test creating a valid instance
        print("Testing valid data:")
        try:
            instance = ModelClass(**valid_data)
            print(f"✓ Valid instance created successfully: {instance}")
            print(f"JSON: {instance.json()}\n")
        except ValidationError as e:
            print(f"✗ ERROR: Valid data was rejected: {e}\n")
            return
        except Exception as e:
            print(f"✗ ERROR: Unexpected error with valid data: {type(e).__name__}: {str(e)}")
            traceback.print_exc()
            return
        
        # Test invalid data samples
        print("Testing invalid data:")
        for i, invalid_data in enumerate(invalid_data_samples, 1):
            print(f"Invalid test #{i}: {invalid_data}")
            try:
                instance = ModelClass(**invalid_data)
                print(f"✗ ERROR: Invalid data was accepted when it should be rejected\n")
            except ValidationError as e:
                print(f"✓ Correctly rejected invalid data: {e}\n")
            except Exception as e:
                print(f"✗ ERROR: Unexpected error with invalid data: {type(e).__name__}: {str(e)}\n")
                traceback.print_exc()
    
    except ImportError as e:
        print(f"Error importing model: {str(e)}")
        traceback.print_exc()
    except Exception as e:
        print(f"Unexpected error: {type(e).__name__}: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_model(sys.argv[1])
    else:
        print("Please specify a model name to test.")
        print("Available models: Tag, AssignedStaff, TranscriptEntry, CategoryModel, TimeSlot")
