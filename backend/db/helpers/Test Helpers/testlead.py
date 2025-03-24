from ..lead.lead_queries import get_lead_with_related_data
from ...connections.database import get_db
import asyncio
async def test_get_lead_with_related_data():
    async with get_db() as db:
        lead = await get_lead_with_related_data(db, "123")
        print(lead)

if __name__ == "__main__":
    asyncio.run(test_get_lead_with_related_data())