import traceback

# Test imports only, no validation

def test_import(module_name):
    print(f"Testing import of {module_name}...")
    try:
        module = __import__(module_name, fromlist=["*"])
        print(f"✓ Successfully imported {module_name}")
        return True
    except Exception as e:
        print(f"✗ Error importing {module_name}: {type(e).__name__}: {str(e)}")
        traceback.print_exc()
        return False

# Common schemas
common_schemas = [
    "app.schemas.common.lead_types",
    "app.schemas.common.call_types",
    "app.schemas.common.appointment_types",
    "app.schemas.common.knowledge_types",
    "app.schemas.common.activity"
]

# Base models
base_schemas = [
    "app.schemas.leads.base",
    "app.schemas.calls.base",
    "app.schemas.appointments.base",
    "app.schemas.knowledge.base"
]

# Response models
response_schemas = [
    "app.schemas.leads.responses",
    "app.schemas.calls.responses",
    "app.schemas.appointments.responses",
    "app.schemas.knowledge.responses",
    "app.schemas.knowledge.sources"
]

if __name__ == "__main__":
    print("=== Testing Common Schemas ===")
    for schema in common_schemas:
        test_import(schema)
        print()
    
    print("\n=== Testing Base Models ===")
    for schema in base_schemas:
        test_import(schema)
        print()
    
    print("\n=== Testing Response Models ===")
    for schema in response_schemas:
        test_import(schema)
        print()
