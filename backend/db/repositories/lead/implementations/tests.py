from .postgres_lead_repository import PostgresLeadRepository
from ....connections.database import get_db
import pprint as pretty_print
import asyncio

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
        
async def test_get_priority_leads():
    async with get_db() as db:
        repo = PostgresLeadRepository(db)
        leads = await repo.get_prioritized_leads("0e523922-dd5d-4571-8e47-433e5dc61ea6", 10)
        pretty_print.pprint(leads)
        
        
if __name__ == "__main__":
    asyncio.run(test_get_priority_leads())