import sys
import importlib
import json
import traceback
from datetime import datetime, timedelta
from pydantic import ValidationError

# Test configuration
VERBOSE = True  # Set to True for detailed output

def log(msg, level="INFO"):
    """Simple logging function"""
    if VERBOSE or level != "INFO":
        print(f"[{level}] {msg}")

def test_schema_module(module_path):
    """Test importing a schema module and its classes"""
    try:
        module = importlib.import_module(module_path)
        log(f"Successfully imported {module_path}")
        return module
    except Exception as e:
        log(f"Error importing {module_path}: {str(e)}", "ERROR")
        traceback.print_exc()
        return None

def test_model_validation(model_class, valid_data, invalid_data_list):
    """Test a Pydantic model with valid and invalid data"""
    log(f"Testing model: {model_class.__name__}")
    
    # Test valid data
    try:
        instance = model_class(**valid_data)
        log(f"  ✓ Valid data accepted")
    except ValidationError as e:
        log(f"  ✗ Valid data rejected: {str(e)}", "ERROR")
        return False
    except Exception as e:
        log(f"  ✗ Unexpected error with valid data: {str(e)}", "ERROR")
        traceback.print_exc()
        return False
    
    # Test each invalid data case
    success = True
    for i, invalid_data in enumerate(invalid_data_list, 1):
        try:
            instance = model_class(**invalid_data)
            log(f"  ✗ Invalid data #{i} accepted when it should be rejected", "ERROR")
            success = False
        except ValidationError as e:
            log(f"  ✓ Invalid data #{i} properly rejected")
        except Exception as e:
            log(f"  ✗ Unexpected error with invalid data #{i}: {str(e)}", "ERROR")
            traceback.print_exc()
            success = False
    
    return success

# ------ Lead Types Testing ------
def test_lead_types():
    try:
        lead_types = test_schema_module("app.schemas.common.lead_types")
        if not lead_types:
            return
        
        # Test Tag model
        valid_tag = {"id": "tag-123", "name": "VIP", "color": "#FF5733"}
        invalid_tags = [
            {"id": "tag-123", "name": "VIP", "color": "invalid-color"},
            {"id": "tag-123", "name": "", "color": "#FF5733"},
            {"id": "", "name": "VIP", "color": "#FF5733"},
        ]
        test_model_validation(lead_types.Tag, valid_tag, invalid_tags)
        
        # Test AssignedStaff model
        valid_staff = {"id": "staff-123", "first_name": "John", "last_name": "Doe"}
        invalid_staff = [
            {"id": "", "first_name": "John", "last_name": "Doe"},
            {"id": "staff-123", "first_name": "", "last_name": "Doe"},
            {"id": "staff-123", "first_name": "John", "last_name": ""},
        ]
        test_model_validation(lead_types.AssignedStaff, valid_staff, invalid_staff)
    except Exception as e:
        log(f"Error in test_lead_types: {str(e)}", "ERROR")
        traceback.print_exc()

# ------ Lead Base Testing ------
def test_lead_base():
    try:
        lead_base = test_schema_module("app.schemas.leads.base")
        if not lead_base:
            return
        
        # Test LeadBase model
        valid_lead = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone": "+1234567890",
            "status": "new",
            "source": "website",
            "notes": "Interested in premium membership",
            "branch_id": "branch-123",
            "interest": "Personal Training",
            "interest_location": "Downtown"
        }
        invalid_leads = [
            # Invalid email
            {**valid_lead, "email": "invalid-email"},
            # Invalid phone
            {**valid_lead, "phone": "123"},
            # Invalid status
            {**valid_lead, "status": "invalid-status"},
        ]
        test_model_validation(lead_base.LeadBase, valid_lead, invalid_leads)
    except Exception as e:
        log(f"Error in test_lead_base: {str(e)}", "ERROR")
        traceback.print_exc()

# ------ Call Base Testing ------
def test_call_base():
    try:
        call_base = test_schema_module("app.schemas.calls.base")
        if not call_base:
            return
        
        # Test CallBase model
        valid_call = {
            "lead_id": "lead-123",
            "direction": "outbound",
            "status": "completed",
            "date": datetime.now().isoformat() + "Z",
            "duration": 300,
            "outcome": "appointment_booked",
            "notes": "Customer was very interested in the premium plan"
        }
        invalid_calls = [
            # Invalid direction
            {**valid_call, "direction": "invalid-direction"},
            # Invalid status
            {**valid_call, "status": "invalid-status"},
            # Invalid outcome
            {**valid_call, "outcome": "invalid-outcome"},
            # Invalid timestamp format
            {**valid_call, "date": "2025-03-15"},
        ]
        test_model_validation(call_base.CallBase, valid_call, invalid_calls)
    except Exception as e:
        log(f"Error in test_call_base: {str(e)}", "ERROR")
        traceback.print_exc()

# ------ Appointment Base Testing ------
def test_appointment_base():
    try:
        appointment_base = test_schema_module("app.schemas.appointments.base")
        if not appointment_base:
            return
        
        # Test AppointmentBase model
        valid_appointment = {
            "lead_id": "lead-123",
            "type": "consultation",
            "date": datetime.now().isoformat() + "Z",
            "duration": 60,
            "status": "scheduled",
            "branch_id": "branch-123",
            "notes": "Initial consultation"
        }
        invalid_appointments = [
            # Invalid type
            {**valid_appointment, "type": "invalid-type"},
            # Invalid status
            {**valid_appointment, "status": "invalid-status"},
            # Invalid timestamp format
            {**valid_appointment, "date": "2025-03-15"},
            # Negative duration
            {**valid_appointment, "duration": -10},
        ]
        test_model_validation(appointment_base.AppointmentBase, valid_appointment, invalid_appointments)
    except Exception as e:
        log(f"Error in test_appointment_base: {str(e)}", "ERROR")
        traceback.print_exc()

# Create a simplified test function that only tests one schema component at a time
def run_single_test(test_name):
    test_functions = {
        "lead_types": test_lead_types,
        "lead_base": test_lead_base,
        "call_base": test_call_base,
        "appointment_base": test_appointment_base
    }
    
    if test_name in test_functions:
        log(f"Running test for {test_name}...")
        test_functions[test_name]()
    else:
        log(f"Test '{test_name}' not found. Available tests: {list(test_functions.keys())}", "ERROR")

# Run specific tests when called with arguments
if __name__ == "__main__":
    if len(sys.argv) > 1:
        for test_name in sys.argv[1:]:
            run_single_test(test_name)
    else:
        # If no arguments are provided, run lead_types test by default
        # This is a simpler approach to start debugging
        log("Running lead_types test by default...")
        test_lead_types()
