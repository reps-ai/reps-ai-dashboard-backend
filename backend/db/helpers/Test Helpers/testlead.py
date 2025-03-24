from ..lead.lead_queries import get_lead_with_related_data
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


async def test_get_lead_with_related_data():
    async with get_db() as db:
        lead = await get_lead_with_related_data(db, "04acec14-f8c0-4a3a-a612-7dde59b9f5da")
        print(lead)

if __name__ == "__main__":
    asyncio.run(test_get_lead_with_related_data())