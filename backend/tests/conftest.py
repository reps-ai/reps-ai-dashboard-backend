"""
Test configuration and shared fixtures.

This file contains pytest fixtures that can be shared across different test modules.
"""
import pytest

def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test that interacts with actual services"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )

def pytest_addoption(parser):
    """Add command-line options to pytest."""
    parser.addoption(
        "--run-integration", 
        action="store_true", 
        default=False, 
        help="run integration tests"
    )

def pytest_collection_modifyitems(config, items):
    """Skip integration tests unless --run-integration is specified."""
    if not config.getoption("--run-integration"):
        skip_integration = pytest.mark.skip(reason="need --run-integration option to run")
        for item in items:
            if "integration" in item.keywords:
                item.add_marker(skip_integration) 