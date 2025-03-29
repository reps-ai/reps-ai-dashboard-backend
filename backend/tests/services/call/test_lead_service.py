"""
Test suite for the DefaultLeadService class.
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch, call, ANY
import uuid

from backend.services.lead.implementation import DefaultLeadService
from backend.db.repositories.lead.interface import LeadRepository

# Test data constants
TEST_LEAD_ID = "00848ea2-6d44-4a52-a552-fc6a26306a4a"
TEST_GYM_ID = "0072ba23-9c82-4dfe-8edf-05279a0ecdc9"
TEST_BRANCH_ID = "632bfb51-70a4-4679-845d-4e399b4ec395"
TEST_CALL_ID = "26aaab03-7521-4d79-b7b6-cf375cc57595"

@pytest.fixture
def mock_lead_repository():
    """Create a mock LeadRepository."""
    repository = AsyncMock(spec=LeadRepository)
    # Add methods that might not be in the interface but are used in tests
    repository.update_lead_qualification = AsyncMock()
    repository.add_tags_to_lead = AsyncMock()
    repository.get_leads_by_status = AsyncMock()
    repository.update_lead_after_call = AsyncMock()
    repository.get_leads_by_branch = AsyncMock()
    repository.get_prioritized_leads = AsyncMock()
    return repository

@pytest.fixture
def lead_service(mock_lead_repository):
    """Create a DefaultLeadService instance with mocked dependencies."""
    return DefaultLeadService(lead_repository=mock_lead_repository)

# 1. GET LEAD TESTS
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "lead_id, lead_exists, expected_error",
    [
        (TEST_LEAD_ID, True, False),
        (TEST_LEAD_ID, False, True),
        ("", False, True),
        (None, False, True),
        (str(uuid.uuid4()), True, False),
    ]
)
async def test_get_lead(lead_service, mock_lead_repository, lead_id, lead_exists, expected_error):
    """Test the get_lead function with various scenarios."""
    print(f"\n=== Testing get_lead with lead_id={lead_id}, exists={lead_exists} ===")
    
    if lead_exists:
        mock_data = {
            "id": lead_id,
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone": "1234567890",
            "status": "new",
            "qualification_score": "hot",
            "created_at": datetime.now() - timedelta(days=10),
            "updated_at": datetime.now() - timedelta(days=2),
        }
        mock_lead_repository.get_lead_by_id.return_value = mock_data
        print("\nMock Data Structure:")
        print(mock_data)
    else:
        mock_lead_repository.get_lead_by_id.return_value = None
        print("\nMock Data: None (Lead does not exist)")
    
    if expected_error:
        print("\nExpecting error to be raised...")
        with pytest.raises(ValueError) as excinfo:
            await lead_service.get_lead(lead_id)
        print(f"Error raised successfully")
    else:
        print("\nCalling service.get_lead...")
        result = await lead_service.get_lead(lead_id)
        print("\nActual Result Structure:")
        print(result)
        
        print("\nPerforming assertions...")
        assert result["id"] == lead_id
        mock_lead_repository.get_lead_by_id.assert_called_once_with(lead_id)
        print("All assertions passed!")

# 2. UPDATE LEAD TESTS
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "lead_id, lead_data, lead_exists, expected_error",
    [
        (TEST_LEAD_ID, {"first_name": "Updated Name"}, True, False),
        (TEST_LEAD_ID, {"status": "contacted"}, True, False),
        (TEST_LEAD_ID, {}, True, False),
        (TEST_LEAD_ID, {"invalid_field": "value"}, True, False),
        (TEST_LEAD_ID, {"first_name": "Updated Name"}, False, True),
        ("", {"first_name": "Updated Name"}, False, True),
        (None, {"first_name": "Updated Name"}, False, True),
    ]
)
async def test_update_lead(lead_service, mock_lead_repository, lead_id, lead_data, lead_exists, expected_error):
    """Test the update_lead function with various scenarios."""
    print(f"\n=== Testing update_lead with lead_id={lead_id}, lead_exists={lead_exists} ===")
    
    print("\nInput Data:")
    print(f"  lead_id: {lead_id}")
    print(f"  lead_data: {lead_data}")
    
    if lead_exists:
        updated_lead = {
            "id": lead_id,
            "first_name": lead_data.get("first_name", "John"),
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone": "1234567890",
            "status": lead_data.get("status", "new"),
            "updated_at": datetime.now()
        }
        mock_lead_repository.update_lead.return_value = updated_lead
        print("\nMocked update_lead response:")
        print(updated_lead)
    else:
        mock_lead_repository.update_lead.return_value = None
        print("\nMocked update_lead response: None")
    
    if expected_error:
        print("\nExpecting error to be raised...")
        with pytest.raises(ValueError) as excinfo:
            await lead_service.update_lead(lead_id, lead_data)
        print(f"Error raised successfully")
    else:
        print("\nCalling service.update_lead...")
        result = await lead_service.update_lead(lead_id, lead_data)
        print("\nActual Result Structure:")
        print(result)
        
        print("\nPerforming assertions...")
        assert result["id"] == lead_id
        # Check that updated_at was added to the data
        lead_data_with_timestamp = {**lead_data, "updated_at": ANY}
        mock_lead_repository.update_lead.assert_called_once_with(lead_id, lead_data_with_timestamp)
        print("All assertions passed!")

# 3. GET PRIORITIZED LEADS TESTS
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "gym_id, count, qualification, exclude_leads, expected_leads",
    [
        (TEST_GYM_ID, 5, "hot", None, [{"id": "lead1"}, {"id": "lead2"}, {"id": "lead3"}, {"id": "lead4"}, {"id": "lead5"}]),
        (TEST_GYM_ID, 3, "neutral", None, [{"id": "lead1"}, {"id": "lead2"}, {"id": "lead3"}]),
        (TEST_GYM_ID, 2, "cold", None, [{"id": "lead1"}, {"id": "lead2"}]),
        (TEST_GYM_ID, 4, None, ["lead1", "lead2"], [{"id": "lead3"}, {"id": "lead4"}, {"id": "lead5"}, {"id": "lead6"}]),
        (TEST_GYM_ID, 0, None, None, []),
        ("invalid-id", 5, "hot", None, []),
    ]
)
async def test_get_prioritized_leads(lead_service, mock_lead_repository, gym_id, count, qualification, exclude_leads, expected_leads):
    """Test the get_prioritized_leads function with various scenarios."""
    print(f"\n=== Testing get_prioritized_leads with gym_id={gym_id}, count={count}, qualification={qualification} ===")
    
    print("\nInput Parameters:")
    print(f"  gym_id: {gym_id}")
    print(f"  count: {count}")
    print(f"  qualification: {qualification}")
    print(f"  exclude_leads: {exclude_leads}")
    
    print("\nExpected Leads:")
    print(expected_leads)
    
    mock_lead_repository.get_prioritized_leads.return_value = expected_leads
    print("\nMocked Repository Response:")
    print(expected_leads)
    
    print("\nCalling service.get_prioritized_leads...")
    result = await lead_service.get_prioritized_leads(gym_id, count, qualification, exclude_leads)
    
    print("\nActual Result:")
    print(result)
    
    print("\nPerforming assertions...")
    assert result == expected_leads
    mock_lead_repository.get_prioritized_leads.assert_called_once_with(
        gym_id=gym_id, count=count, qualification=qualification, exclude_leads=exclude_leads
    )
    print("All assertions passed!")

# 4. UPDATE LEAD AFTER CALL TESTS
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "lead_id, call_data, lead_exists, has_qualification, has_tags, expected_error",
    [
        (TEST_LEAD_ID, {"call_id": TEST_CALL_ID, "outcome": "answered", "notes": "Test call"}, True, False, False, False),
        (TEST_LEAD_ID, {"call_id": TEST_CALL_ID, "outcome": "answered", "qualification": "hot"}, True, True, False, False),
        (TEST_LEAD_ID, {"call_id": TEST_CALL_ID, "outcome": "answered", "tags": ["interested", "follow-up"]}, True, False, True, False),
        (TEST_LEAD_ID, {"call_id": TEST_CALL_ID, "outcome": "answered", "qualification": "hot", "tags": ["interested"]}, True, True, True, False),
        (TEST_LEAD_ID, {}, True, False, False, True),  # Missing call_id
        (TEST_LEAD_ID, {"outcome": "answered"}, True, False, False, True),  # Missing call_id
        (TEST_LEAD_ID, {"call_id": TEST_CALL_ID}, False, False, False, True),  # Lead doesn't exist
    ]
)
async def test_update_lead_after_call(lead_service, mock_lead_repository, lead_id, call_data, lead_exists, has_qualification, has_tags, expected_error):
    """Test the update_lead_after_call function with various scenarios."""
    print(f"\n=== Testing update_lead_after_call with lead_id={lead_id}, has_qualification={has_qualification}, has_tags={has_tags} ===")
    
    print("\nInput Data:")
    print(f"  lead_id: {lead_id}")
    print(f"  call_data: {call_data}")
    
    if lead_exists:
        updated_lead = {
            "id": lead_id,
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone": "1234567890",
            "status": "contacted",
            "qualification_score": call_data.get("qualification", "neutral"),
            "last_called": datetime.now(),
            "updated_at": datetime.now()
        }
        mock_lead_repository.update_lead_after_call.return_value = updated_lead
        mock_lead_repository.update_lead_qualification.return_value = {
            **updated_lead, 
            "qualification_score": call_data.get("qualification", "neutral")
        }
        mock_lead_repository.add_tags_to_lead.return_value = {
            **updated_lead, 
            "tags": call_data.get("tags", [])
        }
        print("\nMocked update_lead_after_call response:")
        print(updated_lead)
    else:
        mock_lead_repository.update_lead_after_call.return_value = None
        print("\nMocked update_lead_after_call response: None")
    
    if expected_error:
        print("\nExpecting error to be raised...")
        with pytest.raises(ValueError) as excinfo:
            await lead_service.update_lead_after_call(lead_id, call_data)
        print(f"Error raised successfully")
    else:
        print("\nCalling service.update_lead_after_call...")
        result = await lead_service.update_lead_after_call(lead_id, call_data)
        print("\nActual Result Structure:")
        print(result)
        
        print("\nPerforming assertions...")
        assert result["id"] == lead_id
        mock_lead_repository.update_lead_after_call.assert_called_once_with(lead_id, call_data)
        
        if has_qualification:
            mock_lead_repository.update_lead_qualification.assert_called_once_with(lead_id, call_data["qualification"])
        else:
            mock_lead_repository.update_lead_qualification.assert_not_called()
            
        if has_tags:
            mock_lead_repository.add_tags_to_lead.assert_called_once_with(lead_id, call_data["tags"])
        else:
            mock_lead_repository.add_tags_to_lead.assert_not_called()
        print("All assertions passed!")

# 5. QUALIFY LEAD TESTS
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "lead_id, qualification, lead_exists, expected_error",
    [
        (TEST_LEAD_ID, "hot", True, False),
        (TEST_LEAD_ID, "cold", True, False),
        (TEST_LEAD_ID, "neutral", True, False),
        (TEST_LEAD_ID, "invalid", True, True),  # Invalid qualification
        (TEST_LEAD_ID, "", True, True),  # Empty qualification
        (TEST_LEAD_ID, None, True, True),  # None qualification
        (TEST_LEAD_ID, "hot", False, True),  # Lead doesn't exist
    ]
)
async def test_qualify_lead(lead_service, mock_lead_repository, lead_id, qualification, lead_exists, expected_error):
    """Test the qualify_lead function with various scenarios."""
    print(f"\n=== Testing qualify_lead with lead_id={lead_id}, qualification={qualification} ===")
    
    print("\nInput Data:")
    print(f"  lead_id: {lead_id}")
    print(f"  qualification: {qualification}")
    
    if lead_exists:
        updated_lead = {
            "id": lead_id,
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone": "1234567890",
            "status": "contacted",
            "qualification_score": qualification,
            "updated_at": datetime.now()
        }
        mock_lead_repository.update_lead_qualification.return_value = updated_lead
        print("\nMocked update_lead_qualification response:")
        print(updated_lead)
    else:
        mock_lead_repository.update_lead_qualification.return_value = None
        print("\nMocked update_lead_qualification response: None")
    
    if expected_error:
        print("\nExpecting error to be raised...")
        with pytest.raises(ValueError) as excinfo:
            await lead_service.qualify_lead(lead_id, qualification)
        print(f"Error raised successfully")
    else:
        print("\nCalling service.qualify_lead...")
        result = await lead_service.qualify_lead(lead_id, qualification)
        print("\nActual Result Structure:")
        print(result)
        
        print("\nPerforming assertions...")
        assert result["id"] == lead_id
        assert result["qualification_score"] == qualification
        mock_lead_repository.update_lead_qualification.assert_called_once_with(lead_id, qualification)
        print("All assertions passed!")

# 6. ADD TAGS TO LEAD TESTS
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "lead_id, tags, lead_exists, expected_error",
    [
        (TEST_LEAD_ID, ["interested", "follow-up"], True, False),
        (TEST_LEAD_ID, ["single-tag"], True, False),
        (TEST_LEAD_ID, [], True, False),  # Empty tags
        (TEST_LEAD_ID, None, True, False),  # None tags
        (TEST_LEAD_ID, ["interested", "follow-up"], False, True),  # Lead doesn't exist
    ]
)
async def test_add_tags_to_lead(lead_service, mock_lead_repository, lead_id, tags, lead_exists, expected_error):
    """Test the add_tags_to_lead function with various scenarios."""
    print(f"\n=== Testing add_tags_to_lead with lead_id={lead_id}, tags={tags} ===")
    
    print("\nInput Data:")
    print(f"  lead_id: {lead_id}")
    print(f"  tags: {tags}")
    
    lead_data = {
        "id": lead_id,
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone": "1234567890",
        "status": "contacted",
        "updated_at": datetime.now()
    }
    
    if lead_exists:
        if tags:
            updated_lead = {**lead_data, "tags": tags}
            mock_lead_repository.add_tags_to_lead.return_value = updated_lead
            print("\nMocked add_tags_to_lead response:")
            print(updated_lead)
        else:
            # If no tags, get_lead is called instead
            mock_lead_repository.get_lead_by_id.return_value = lead_data
            print("\nMocked get_lead_by_id response (no tags):")
            print(lead_data)
    else:
        mock_lead_repository.add_tags_to_lead.return_value = None
        print("\nMocked add_tags_to_lead response: None")
    
    if expected_error:
        print("\nExpecting error to be raised...")
        with pytest.raises(ValueError) as excinfo:
            await lead_service.add_tags_to_lead(lead_id, tags)
        print(f"Error raised successfully")
    else:
        print("\nCalling service.add_tags_to_lead...")
        result = await lead_service.add_tags_to_lead(lead_id, tags)
        print("\nActual Result Structure:")
        print(result)
        
        print("\nPerforming assertions...")
        assert result["id"] == lead_id
        if tags:
            mock_lead_repository.add_tags_to_lead.assert_called_once_with(lead_id, tags)
        else:
            mock_lead_repository.get_lead_by_id.assert_called_once_with(lead_id)
        print("All assertions passed!")

# 7. GET LEADS BY STATUS TESTS
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "gym_id, status, expected_leads",
    [
        (TEST_GYM_ID, "new", [{"id": "lead1", "status": "new"}, {"id": "lead2", "status": "new"}]),
        (TEST_GYM_ID, "contacted", [{"id": "lead3", "status": "contacted"}, {"id": "lead4", "status": "contacted"}]),
        (TEST_GYM_ID, "qualified", [{"id": "lead5", "status": "qualified"}]),
        (TEST_GYM_ID, "converted", []),  # No converted leads
        ("invalid-id", "new", []),  # Invalid gym id
    ]
)
async def test_get_leads_by_status(lead_service, mock_lead_repository, gym_id, status, expected_leads):
    """Test the get_leads_by_status function with various scenarios."""
    print(f"\n=== Testing get_leads_by_status with gym_id={gym_id}, status={status} ===")
    
    print("\nInput Parameters:")
    print(f"  gym_id: {gym_id}")
    print(f"  status: {status}")
    
    print("\nExpected Leads:")
    print(expected_leads)
    
    mock_lead_repository.get_leads_by_status.return_value = expected_leads
    print("\nMocked Repository Response:")
    print(expected_leads)
    
    print("\nCalling service.get_leads_by_status...")
    result = await lead_service.get_leads_by_status(gym_id, status)
    
    print("\nActual Result:")
    print(result)
    
    print("\nPerforming assertions...")
    assert result == expected_leads
    mock_lead_repository.get_leads_by_status.assert_called_once_with(gym_id, status)
    print("All assertions passed!")

# 8. GET PAGINATED LEADS TESTS
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "branch_id, page, page_size, filters, expected_result",
    [
        (TEST_BRANCH_ID, 1, 50, None, {"leads": [{"id": "lead1"}, {"id": "lead2"}], "pagination": {"total": 2, "page": 1, "page_size": 50, "pages": 1}}),
        (TEST_BRANCH_ID, 2, 10, {"status": "new"}, {"leads": [{"id": "lead11"}, {"id": "lead12"}], "pagination": {"total": 15, "page": 2, "page_size": 10, "pages": 2}}),
        (TEST_BRANCH_ID, 1, 50, {"qualification": "hot"}, {"leads": [{"id": "lead1", "qualification": "hot"}], "pagination": {"total": 1, "page": 1, "page_size": 50, "pages": 1}}),
        (TEST_BRANCH_ID, 1, 5, {"search": "john"}, {"leads": [{"id": "lead1", "first_name": "John"}], "pagination": {"total": 1, "page": 1, "page_size": 5, "pages": 1}}),
        (TEST_BRANCH_ID, 1, 50, {}, {"leads": [], "pagination": {"total": 0, "page": 1, "page_size": 50, "pages": 0}}),  # No leads
        ("invalid-id", 1, 50, None, {"leads": [], "pagination": {"total": 0, "page": 1, "page_size": 50, "pages": 0}}),  # Invalid branch id
    ]
)
async def test_get_paginated_leads(lead_service, mock_lead_repository, branch_id, page, page_size, filters, expected_result):
    """Test the get_paginated_leads function with various scenarios."""
    print(f"\n=== Testing get_paginated_leads with branch_id={branch_id}, page={page}, page_size={page_size} ===")
    
    print("\nInput Parameters:")
    print(f"  branch_id: {branch_id}")
    print(f"  page: {page}")
    print(f"  page_size: {page_size}")
    print(f"  filters: {filters}")
    
    print("\nExpected Result:")
    print(expected_result)
    
    mock_lead_repository.get_leads_by_branch.return_value = expected_result
    print("\nMocked Repository Response:")
    print(expected_result)
    
    print("\nCalling service.get_paginated_leads...")
    result = await lead_service.get_paginated_leads(branch_id, page, page_size, filters)
    
    print("\nActual Result:")
    print(result)
    
    print("\nPerforming assertions...")
    assert result == expected_result
    mock_lead_repository.get_leads_by_branch.assert_called_once_with(
        branch_id=branch_id, page=page, page_size=page_size, filters=filters
    )
    print("All assertions passed!")