from .postgres_call_repository import PostgresCallRepository
from ....connections.database import get_db
import pprint as pretty_print
import asyncio
from datetime import datetime, timedelta
from uuid import UUID

# Test data constants
CALL_ID = "151f50a5-ec26-4673-98c9-a6137c3581a0"
LEAD_ID = "00848ea2-6d44-4a52-a552-fc6a26306a4a"
CAMPAIGN_ID = "822043ad-260f-4e04-bf4e-35cd8cdb39fe"
BRANCH_ID = "0e523922-dd5d-4571-8e47-433e5dc61ea6"
GYM_ID = "242079fc-0848-4f29-bd3b-698c94860efb"

#Works
async def test_create_call():
    async with get_db() as db:
        repo = PostgresCallRepository(db)
        call_data = {
            "lead_id": UUID(LEAD_ID),
            "campaign_id": UUID(CAMPAIGN_ID),
            "branch_id": UUID(BRANCH_ID),
            "gym_id": UUID(GYM_ID),
            "call_status": "completed",
            "start_time": datetime.now() - timedelta(minutes=5),
            "end_time": datetime.now(),
            "duration": 300,  # 5 minutes in seconds
            "outcome": "answered",
            "human_notes": "Test call for new lead",
            "call_type": "outbound"  # Required field
        }
        call = await repo.create_call(call_data)
        pretty_print.pprint(call)
        return call  # Return for use in delete test

#Works
async def test_get_call_by_id():
    async with get_db() as db:
        repo = PostgresCallRepository(db)
        call = await repo.get_call_by_id(UUID(CALL_ID))
        pretty_print.pprint(call)

#Works
async def test_update_call():
    async with get_db() as db:
        repo = PostgresCallRepository(db)
        updated_data = {
            "human_notes": "Updated call notes",
            "outcome": "successful",
            "duration": 325  # Updated duration
        }
        updated_call = await repo.update_call(UUID(CALL_ID), updated_data)
        pretty_print.pprint(updated_call)

#Works
async def test_delete_call():
    # First create a temporary call to delete
    temp_call = await test_create_call()
    
    async with get_db() as db:
        repo = PostgresCallRepository(db)
        result = await repo.delete_call(temp_call["id"])
        print(f"Delete result: {result}")

#Errors 
async def test_get_calls_by_campaign():
    async with get_db() as db:
        repo = PostgresCallRepository(db)
        calls = await repo.get_calls_by_campaign(UUID(CAMPAIGN_ID))
        pretty_print.pprint(calls)

#Works
async def test_get_calls_by_lead():
    async with get_db() as db:
        repo = PostgresCallRepository(db)
        calls = await repo.get_calls_by_lead(UUID(LEAD_ID))
        pretty_print.pprint(calls)

#Works
async def test_get_calls_by_date_range():
    async with get_db() as db:
        repo = PostgresCallRepository(db)
        start_date = datetime.now() - timedelta(days=1000)
        end_date = datetime.now()
        calls = await repo.get_calls_by_date_range(
            UUID(BRANCH_ID), 
            start_date, 
            end_date
        )
        pretty_print.pprint(calls)

#Works
async def test_get_calls_by_outcome():
    async with get_db() as db:
        repo = PostgresCallRepository(db)
        
        # First create a call with a specific outcome
        call_data = {
            "lead_id": UUID(LEAD_ID),
            "campaign_id": UUID(CAMPAIGN_ID),
            "branch_id": UUID(BRANCH_ID),
            "gym_id": UUID(GYM_ID),
            "call_status": "completed",
            "start_time": datetime.now() - timedelta(minutes=5),
            "end_time": datetime.now(),
            "duration": 300,
            "outcome": "test_outcome",  # Specific outcome to search for
            "human_notes": "Test call for outcome testing",
            "call_type": "outbound"
        }
        
        # Create the test call
        created_call = await repo.create_call(call_data)
        print(f"Created test call with ID: {created_call['id']} and outcome: {created_call['outcome']}")
        
        # Now search for calls with this outcome
        calls = await repo.get_calls_by_outcome(
            UUID(BRANCH_ID),
            "test_outcome"  # Use the same outcome as created call
        )
        
        pretty_print.pprint(calls)
        
        # Clean up - delete the test call
        await repo.delete_call(created_call["id"])

# Main test runner function
async def run_tests():
    test_functions = {
        "1": (test_create_call, "Create new call"),
        "2": (test_get_call_by_id, "Get call by ID"),
        "3": (test_update_call, "Update call"),
        "4": (test_delete_call, "Delete call"),
        "5": (test_get_calls_by_campaign, "Get calls by campaign"),
        "6": (test_get_calls_by_lead, "Get calls by lead"),
        "7": (test_get_calls_by_date_range, "Get calls by date range"),
        "8": (test_get_calls_by_outcome, "Get calls by outcome")
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
