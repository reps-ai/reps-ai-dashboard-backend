from ..lead.lead_queries import (get_lead_with_related_data, get_leads_by_gym_with_filters, create_lead_db, update_lead_db, delete_lead_db, get_converted_leads_db, get_lead_conversion_details_db, get_leads_by_assigned_user_db, build_lead_filters, get_leads_by_gym_with_filters, update_lead_after_call_db, get_prioritized_leads_db, get_leads_for_retry_db)
from ...connections.database import get_db
from ...models.lead import Lead
from ...models.gym.branch import Branch
from ...models.gym.gym import Gym
from ...models.user import User
from ...models.lead.tag import Tag
from ...models.appointment import Appointment
from ...models.call.call_log import CallLog
from ...models.call.follow_up_call import FollowUpCall
from ...models.member import Member
from ...models.campaign.follow_up_campaign import FollowUpCampaign
import asyncio
import pprint as pretty_print


async def test_get_lead_with_related_data():
    async with get_db() as db:
        lead = await get_lead_with_related_data(db, "00848ea2-6d44-4a52-a552-fc6a26306a4a")
        pretty_print.pprint(lead)

async def test_get_leads_by_gym_with_filters():
    async with get_db() as db:
        leads = await get_leads_by_gym_with_filters(db, "0e523922-dd5d-451-8e47-433e5dc61ea6")
        pretty_print.pprint(leads)

async def test_create_lead_db():
    async with get_db() as db:
        lead_data = {
            "branch_id": "0e523922-dd5d-4571-8e47-433e5dc61ea6",
            "gym_id": "0072ba23-9c82-4dfe-8edf-05279a0ecdc9",  # Using same ID for testing
            "first_name": "John",
            "last_name": "Doe",
            "phone": "1234567890",
            "email": "john.doe@example.com",
            "lead_status": "new",
            "notes": "Test lead created for testing",
            "interest": "Weight training",
            "interest_location": "Local area",
            "fitness_goals": "Lose weight and build muscle",
            "budget_range": "$50-100",
            "timeframe": "1-3 months",
            "preferred_contact_method": "phone",
            "preferred_contact_time": "evenings",
            "urgency": "medium",
            "qualification_score": 7,
            "qualification_notes": "Seems very interested",
            "fitness_level": "beginner",
            "previous_gym_experience": True,
            "specific_health_goals": "Reduce blood pressure",
            "preferred_training_type": "personal training",
            "availability": "weekday evenings, weekend mornings",
            "medical_conditions": "None"
        }
        
        lead = await create_lead_db(db, lead_data)
        pretty_print.pprint(lead)

async def test_update_lead_db():
    async with get_db() as db:
        lead_data = {
            "branch_id": "0e523922-dd5d-4571-8e47-433e5dc61ea6",
            "gym_id": "0072ba23-9c82-4dfe-8edf-05279a0ecdc9",  # Using same ID for testing
            "first_name": "John",
            "last_name": "Doe",
            "phone": "1234567890",
            "email": "john.doe@example.com",
            "lead_status": "new",
            "notes": "Test lead was UPDATED",
        }
        lead = await update_lead_db(db, "7d6b7b7e-047f-40f7-aa71-221435df4417", lead_data)
        pretty_print.pprint(lead)

async def test_delete_lead_db():
    async with get_db() as db:
        lead = await delete_lead_db(db, "7d6b7b7e-047f-40f7-aa71-221435df4417")
        pretty_print.pprint(lead)

async def test_get_prioritized_leads_db():
    async with get_db() as db:
        leads = await get_prioritized_leads_db(db, "0e523922-dd5d-4571-8e47-433e5dc61ea6", 10)
        pretty_print.pprint(leads)

if __name__ == "__main__":
    asyncio.run(test_get_prioritized_leads_db())