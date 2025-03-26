from .postgres_lead_repository import PostgresLeadRepository
from ....connections.database import get_db
import pprint as pretty_print
import asyncio
from datetime import datetime, timedelta

async def test_get_leads_by_branch():
    async with get_db() as db:
        repo = PostgresLeadRepository(db)
        leads = await repo.get_leads_by_branch("0e523922-dd5d-4571-8e47-433e5dc61ea6")
        pretty_print.pprint(leads)

async def test_get_lead_by_id():
    async with get_db() as db:
        repo = PostgresLeadRepository(db)
        lead = await repo.get_lead_by_id("00848ea2-6d44-4a52-a552-fc6a26306a4a")
        pretty_print.pprint(lead)

async def test_create_lead():
    async with get_db() as db:
        repo = PostgresLeadRepository(db)
        lead = await repo.create_lead({
            "first_name": "Aditya",  # required
            "last_name": "Bhaskara",   # required
            "phone": "5556789",       # required
            "branch_id": "906d6e74-afce-4490-9c92-c9b1c9a91163",   # required
            "gym_id": "242079fc-0848-4f29-bd3b-698c94860efb",      # required
            # Optional fields below
            "email": "",
            "lead_status": "new",  # defaults to "new"
            "assigned_to_user_id": None,
            "notes": None,
            "interest": None,
            "interest_location": None,
            "score": None,
            "source": None,
            "fitness_goals": None,
            "budget_range": None,
            "timeframe": None,
            "preferred_contact_method": None,
            "preferred_contact_time": None,
            "urgency": None,
            "qualification_score": None,
            "qualification_notes": None,
            "fitness_level": None,
            "previous_gym_experience": None,
            "specific_health_goals": None,
            "preferred_training_type": None,
            "availability": None,
            "medical_conditions": None
        })
        pretty_print.pprint(lead)

async def test_update_lead():
    async with get_db() as db:
        repo = PostgresLeadRepository(db)
        updated_lead = await repo.update_lead("00848ea2-6d44-4a52-a552-fc6a26306a4a", {
            "first_name": "Updated Name",
            "notes": "Test update notes",
            "fitness_goals": "Weight loss"
        })
        pretty_print.pprint(updated_lead)

async def test_delete_lead():
    async with get_db() as db:
        repo = PostgresLeadRepository(db)
        # Create a temporary lead for deletion testing
        temp_lead = await repo.create_lead({
            "first_name": "Delete",
            "last_name": "Test",
            "phone": "5559999",
            "branch_id": "906d6e74-afce-4490-9c92-c9b1c9a91163",
            "gym_id": "242079fc-0848-4f29-bd3b-698c94860efb",
        })
        # Now delete it
        result = await repo.delete_lead(temp_lead["id"])
        print(f"Delete result: {result}")

async def test_get_leads_by_qualification():
    async with get_db() as db:
        repo = PostgresLeadRepository(db)
        leads = await repo.get_leads_by_qualification("242079fc-0848-4f29-bd3b-698c94860efb", "qualified")
        pretty_print.pprint(leads)

async def test_update_lead_qualification():
    async with get_db() as db:
        repo = PostgresLeadRepository(db)
        lead = await repo.update_lead_qualification("00848ea2-6d44-4a52-a552-fc6a26306a4a", "qualified")
        pretty_print.pprint(lead)

async def test_add_tags_to_lead():
    async with get_db() as db:
        repo = PostgresLeadRepository(db)
        updated_lead = await repo.add_tags_to_lead(
            "00848ea2-6d44-4a52-a552-fc6a26306a4a", 
            ["interested", "follow-up", "hot-lead"]
        )
        pretty_print.pprint(updated_lead)

async def test_remove_tags_from_lead():
    async with get_db() as db:
        repo = PostgresLeadRepository(db)
        # First add a tag that we'll remove
        await repo.add_tags_to_lead(
            "00848ea2-6d44-4a52-a552-fc6a26306a4a", 
            ["test-tag-to-remove"]
        )
        # Now remove it
        updated_lead = await repo.remove_tags_from_lead(
            "00848ea2-6d44-4a52-a552-fc6a26306a4a", 
            ["interested"]
        )
        pretty_print.pprint(updated_lead)

async def test_update_lead_after_call():
    async with get_db() as db:
        repo = PostgresLeadRepository(db)
        call_data = {
            "call_duration": 120,  # in seconds
            "call_outcome": "answered",
            "qualification": "qualified",
            "notes": "Lead showed interest in premium membership",
            "next_call_date": (datetime.now() + timedelta(days=2)).isoformat(),
            "follow_up_action": "schedule_tour"
        }
        updated_lead = await repo.update_lead_after_call(
            "00848ea2-6d44-4a52-a552-fc6a26306a4a", 
            call_data
        )
        pretty_print.pprint(updated_lead)

async def test_get_lead_call_history():
    async with get_db() as db:
        repo = PostgresLeadRepository(db)
        call_history = await repo.get_lead_call_history("00848ea2-6d44-4a52-a552-fc6a26306a4a")
        pretty_print.pprint(call_history)

async def test_get_priority_leads():
    async with get_db() as db:
        repo = PostgresLeadRepository(db)
        leads = await repo.get_prioritized_leads("0e523922-dd5d-4571-8e47-433e5dc61ea6", 10)
        pretty_print.pprint(leads)

async def test_get_leads_for_retry():
    async with get_db() as db:
        repo = PostgresLeadRepository(db)
        # Replace with valid campaign_id
        leads = await repo.get_leads_for_retry("campaign-id-placeholder", 3)
        pretty_print.pprint(leads)

async def test_update_lead_notes():
    async with get_db() as db:
        repo = PostgresLeadRepository(db)
        updated_lead = await repo.update_lead_notes(
            "00848ea2-6d44-4a52-a552-fc6a26306a4a", 
            "New detailed notes about this lead's interests and historyyyyy."
        )
        pretty_print.pprint(updated_lead)

async def test_get_leads_by_status():
    async with get_db() as db:
        repo = PostgresLeadRepository(db)
        leads = await repo.get_leads_by_status(
            "0e523922-dd5d-4571-8e47-433e5dc61ea6",
            "new"
        )
        pretty_print.pprint(leads)

async def test_update_lead_status():
    async with get_db() as db:
        repo = PostgresLeadRepository(db)
        updated_lead = await repo.update_lead_status(
            "00848ea2-6d44-4a52-a552-fc6a26306a4a", 
            "newww"
        )
        pretty_print.pprint(updated_lead)

# Main test runner function
async def run_tests():
    test_functions = {
        "1": (test_get_leads_by_branch, "Get leads by branch"),
        "2": (test_get_lead_by_id, "Get lead by ID"),
        "3": (test_create_lead, "Create new lead"),
        "4": (test_update_lead, "Update lead"),
        "5": (test_delete_lead, "Delete lead"),
        "6": (test_get_leads_by_qualification, "Get leads by qualification"),
        "7": (test_update_lead_qualification, "Update lead qualification"),
        "8": (test_add_tags_to_lead, "Add tags to lead"),
        "9": (test_remove_tags_from_lead, "Remove tags from lead"),
        "10": (test_update_lead_after_call, "Update lead after call"),
        "11": (test_get_lead_call_history, "Get lead call history"),
        "12": (test_get_priority_leads, "Get prioritized leads"),
        "13": (test_get_leads_for_retry, "Get leads for retry"),
        "14": (test_update_lead_notes, "Update lead notes"),
        "15": (test_get_leads_by_status, "Get leads by status"),
        "16": (test_update_lead_status, "Update lead status")
    }
    
    print("Available tests:")
    for key, (_, name) in test_functions.items():
        print(f"{key}: {name}")
    
    choice = input("\nEnter test number to run (or 'all' to run all tests): ")
    
    if choice.lower() == 'all':
        for _, (test_func, name) in test_functions.items():
            print(f"\n--- Running: {name} ---")
            await test_func()
    elif choice in test_functions:
        test_func, name = test_functions[choice]
        print(f"\n--- Running: {name} ---")
        await test_func()
    else:
        print("Invalid choice")

if __name__ == "__main__":
    asyncio.run(run_tests())