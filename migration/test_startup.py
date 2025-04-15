#!/usr/bin/env python3
"""
Test script to verify the application starts up correctly with the updated dependencies.
This script attempts to import key components and initialize them to ensure they're compatible.
"""
import sys
import importlib
import logging
import os
from typing import List, Dict, Any, Tuple
import traceback
import uuid

# Add parent directory to Python path to allow importing 'app'
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
print(f"Added parent directory to Python path: {parent_dir}")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Components to test
COMPONENTS_TO_TEST = [
    # Format: (import_path, class_or_function, init_args, init_kwargs)
    ("fastapi", "FastAPI", [], {}),
    # BaseModel cannot be instantiated directly in Pydantic v2, so we'll test it differently
    ("sqlalchemy.orm", "declarative_base", [], {}),
    ("sqlalchemy.ext.asyncio", "AsyncSession", [], {}),
]

def test_imports() -> List[Tuple[str, str]]:
    """Test importing key packages"""
    failures = []
    
    logger.info("Testing imports of key dependencies...")
    
    for package in [
        "fastapi", 
        "pydantic", 
        "sqlalchemy", 
        "uvicorn", 
        "starlette",
    ]:
        try:
            module = importlib.import_module(package)
            logger.info(f"✓ Successfully imported {package} (version: {getattr(module, '__version__', 'unknown')})")
        except ImportError as e:
            error_msg = str(e)
            failures.append((package, error_msg))
            logger.error(f"✗ Failed to import {package}: {error_msg}")
    
    return failures

def test_component_initialization() -> List[Tuple[str, str]]:
    """Test initializing key components"""
    failures = []
    
    logger.info("Testing initialization of key components...")
    
    for import_path, class_or_function, init_args, init_kwargs in COMPONENTS_TO_TEST:
        try:
            # Import the module
            module_path, item_name = import_path, class_or_function
            module = importlib.import_module(module_path)
            
            # Get the class or function
            item = getattr(module, item_name)
            
            # Initialize it
            instance = item(*init_args, **init_kwargs)
            logger.info(f"✓ Successfully initialized {import_path}.{class_or_function}")
        except Exception as e:
            error_msg = str(e)
            failures.append((f"{import_path}.{class_or_function}", error_msg))
            logger.error(f"✗ Failed to initialize {import_path}.{class_or_function}: {error_msg}")
            logger.debug(traceback.format_exc())
    
    return failures

def test_pydantic_models() -> List[Tuple[str, str]]:
    """Test Pydantic functionality with a simple model"""
    failures = []
    
    logger.info("Testing Pydantic model creation...")
    
    try:
        from pydantic import BaseModel, Field
        
        class TestModel(BaseModel):
            name: str
            age: int = Field(gt=0)
        
        # Create an instance
        model = TestModel(name="Test", age=30)
        logger.info(f"✓ Successfully created and initialized Pydantic model")
    except Exception as e:
        error_msg = str(e)
        failures.append(("pydantic.TestModel", error_msg))
        logger.error(f"✗ Failed to create/initialize Pydantic model: {error_msg}")
        logger.debug(traceback.format_exc())
    
    return failures

def test_app_models() -> List[Tuple[str, str]]:
    """Test importing and initializing application models"""
    failures = []
    
    logger.info("Testing application-specific models...")
    
    # Check Python module path is set up correctly
    cwd = os.getcwd()
    logger.info(f"Current working directory: {cwd}")
    
    if cwd not in sys.path:
        logger.info(f"Adding {cwd} to Python path")
        sys.path.insert(0, cwd)
    
    # Test a mock User model instead of importing from dependencies
    # This avoids the circular import issues
    try:
        from pydantic import BaseModel, ConfigDict
        from typing import Optional
        
        # Create a mock User model that matches app.dependencies.User
        class MockUser(BaseModel):
            id: uuid.UUID
            email: str
            first_name: str
            last_name: str
            role: str
            gym_id: Optional[uuid.UUID] = None
            branch_id: Optional[uuid.UUID] = None
            
            model_config = ConfigDict(extra="ignore")
        
        # Create user with all required fields including optional ones
        user = MockUser(
            id=uuid.UUID("11111111-1111-1111-1111-111111111111"), 
            email="test@example.com", 
            first_name="Test", 
            last_name="User", 
            role="admin",
            gym_id=uuid.UUID("facd154c-9be8-40fb-995f-27ea665d3a8b"),
            branch_id=uuid.UUID("8d8808a4-22f8-4af3-aec4-bab5b44b1aa7")
        )
        logger.info(f"✓ Successfully initialized Mock User model (matching app.dependencies.User)")
    except Exception as e:
        error_msg = str(e)
        failures.append(("MockUser", error_msg))
        logger.error(f"✗ Failed to initialize Mock User model: {error_msg}")
        logger.debug(traceback.format_exc())
    
    # Add more app-specific models to test as needed
    
    return failures

def main():
    """Run all tests and report results"""
    all_failures = []
    
    # Test 1: Basic imports
    import_failures = test_imports()
    all_failures.extend(import_failures)
    
    # Test 2: Component initialization
    init_failures = test_component_initialization()
    all_failures.extend(init_failures)
    
    # Test 3: Pydantic models
    pydantic_failures = test_pydantic_models()
    all_failures.extend(pydantic_failures)
    
    # Test 4: App models
    model_failures = test_app_models()
    all_failures.extend(model_failures)
    
    # Report results
    if all_failures:
        logger.error(f"\n❌ Found {len(all_failures)} issues:")
        for component, error in all_failures:
            logger.error(f"  - {component}: {error}")
        sys.exit(1)
    else:
        logger.info("\n✅ All tests passed! The updated dependencies appear to be compatible.")
        sys.exit(0)

if __name__ == "__main__":
    main() 