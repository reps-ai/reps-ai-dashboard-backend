import pytest
from unittest.mock import AsyncMock, ANY
from backend.services.lead.implementation import DefaultLeadService

@pytest.fixture
def mock_lead_repository():
    mock_repo = AsyncMock()
    mock_repo.get_lead_by_id = AsyncMock(return_value={"id": "lead_123", "name": "Test Lead"})
    mock_repo.update_lead = AsyncMock(return_value={"id": "lead_123", "name": "Updated Lead"})
    mock_repo.get_prioritized_leads = AsyncMock(return_value=[{"id": "lead_1"}, {"id": "lead_2"}])
    mock_repo.update_lead_after_call = AsyncMock(return_value={"id": "lead_123", "updated": True})
    mock_repo.update_lead_qualification = AsyncMock(return_value={"id": "lead_123", "qualification": "hot"})
    mock_repo.add_tags_to_lead = AsyncMock(return_value={"id": "lead_123", "tags": ["new_tag"]})
    mock_repo.get_leads_by_status = AsyncMock(return_value=[{"id": "lead_1"}, {"id": "lead_2"}])
    mock_repo.get_leads_by_branch = AsyncMock(return_value={"leads": [{"id": "lead_1"}], "pagination": {"total": 1, "page": 1}})
    return mock_repo

@pytest.fixture
def lead_service(mock_lead_repository):
    return DefaultLeadService(lead_repository=mock_lead_repository)

@pytest.mark.asyncio
async def test_get_lead(lead_service, mock_lead_repository):
    print("Running test_get_lead...")
    lead = await lead_service.get_lead("lead_123")
    print("Lead Retrieved:", lead)
    assert lead == {"id": "lead_123", "name": "Test Lead"}
    mock_lead_repository.get_lead_by_id.assert_called_once_with("lead_123")

@pytest.mark.asyncio
async def test_update_lead(lead_service, mock_lead_repository):
    print("Running test_update_lead...")
    lead = await lead_service.update_lead("lead_123", {"name": "Updated Lead"})
    print("Lead Updated:", lead)
    assert lead["name"] == "Updated Lead"
    mock_lead_repository.update_lead.assert_called_once_with("lead_123", {"name": "Updated Lead", "updated_at": ANY})

@pytest.mark.asyncio
async def test_get_prioritized_leads(lead_service, mock_lead_repository):
    print("Running test_get_prioritized_leads...")
    leads = await lead_service.get_prioritized_leads("gym_001", 2, "hot", ["lead_5"])
    print("Prioritized Leads:", leads)
    assert len(leads) == 2
    mock_lead_repository.get_prioritized_leads.assert_called_once_with(
        gym_id="gym_001", count=2, qualification="hot", exclude_leads=["lead_5"]
    )

@pytest.mark.asyncio
async def test_update_lead_after_call(lead_service, mock_lead_repository):
    print("Running test_update_lead_after_call...")
    call_data = {"call_id": "call_456", "outcome": "success", "tags": ["interested"], "qualification": "hot"}
    lead = await lead_service.update_lead_after_call("lead_123", call_data)
    print("Lead After Call Update:", lead)
    assert lead["updated"] is True
    mock_lead_repository.update_lead_after_call.assert_called_once_with("lead_123", call_data)
    mock_lead_repository.update_lead_qualification.assert_called_once_with("lead_123", "hot")
    mock_lead_repository.add_tags_to_lead.assert_called_once_with("lead_123", ["interested"])

@pytest.mark.asyncio
async def test_qualify_lead(lead_service, mock_lead_repository):
    print("Running test_qualify_lead...")
    lead = await lead_service.qualify_lead("lead_123", "hot")
    print("Lead Qualification Updated:", lead)
    assert lead["qualification"] == "hot"
    mock_lead_repository.update_lead_qualification.assert_called_once_with("lead_123", "hot")

@pytest.mark.asyncio
async def test_add_tags_to_lead(lead_service, mock_lead_repository):
    print("Running test_add_tags_to_lead...")
    lead = await lead_service.add_tags_to_lead("lead_123", ["new_tag"])
    print("Lead Tags Updated:", lead)
    assert "new_tag" in lead["tags"]
    mock_lead_repository.add_tags_to_lead.assert_called_once_with("lead_123", ["new_tag"])

@pytest.mark.asyncio
async def test_get_leads_by_status(lead_service, mock_lead_repository):
    print("Running test_get_leads_by_status...")
    leads = await lead_service.get_leads_by_status("gym_001", "active")
    print("Leads By Status:", leads)
    assert len(leads) == 2
    mock_lead_repository.get_leads_by_status.assert_called_once_with("gym_001", "active")

@pytest.mark.asyncio
async def test_get_paginated_leads(lead_service, mock_lead_repository):
    print("Running test_get_paginated_leads...")
    result = await lead_service.get_paginated_leads("branch_001", 1, 10, {"status": "active"})
    print("Paginated Leads Result:", result)
    assert "leads" in result
    assert "pagination" in result
    mock_lead_repository.get_leads_by_branch.assert_called_once_with(
        branch_id="branch_001", page=1, page_size=10, filters={"status": "active"}
    )