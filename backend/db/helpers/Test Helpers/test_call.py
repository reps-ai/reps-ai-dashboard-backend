from ...connections.database import get_db
from ...helpers.call.call_queries import (get_call_with_related_data, get_calls_by_campaign_db, get_calls_by_lead_db, get_calls_by_date_range_db, get_calls_by_status_db, get_calls_by_outcome_db, update_call_metrics_db, create_call_log_db, update_call_log_db, delete_call_log_db, get_follow_up_call_db, create_follow_up_call_db, update_follow_up_call_db, delete_follow_up_call_db, get_follow_up_calls_by_campaign_db, get_follow_up_calls_by_lead_db)
import asyncio
import pprint as pretty_print
import datetime

async def test_get_call_with_related_data():
    async with get_db() as db:
        call = await get_call_with_related_data(db, "0e6164f3-1447-40cf-b311-ce042428253a")
        pretty_print.pprint(call)

async def test_get_calls_by_campaign_db():
    async with get_db() as db:
        calls = await get_calls_by_campaign_db(db, "a2b87087-4a35-4be5-8919-b0937e6b4eac")
        pretty_print.pprint(calls)

async def test_get_calls_by_lead_db():
    async with get_db() as db:
        calls = await get_calls_by_lead_db(db, "bf762faa-888e-4986-810d-1d31a7687f91")
        pretty_print.pprint(calls)

async def test_get_calls_by_date_range_db():
    async with get_db() as db:
        calls = await get_calls_by_date_range_db(db, "242079fc-0848-4f29-bd3b-698c94860efb", datetime.datetime(2024, 3, 25, 11, 7, 0), datetime.datetime(2026, 3, 25, 11, 7, 0))
        pretty_print.pprint(calls)

async def test_get_calls_by_status_db():
    async with get_db() as db:
        calls = await get_calls_by_status_db(db, "242079fc-0848-4f29-bd3b-698c94860efb", "failed", datetime.datetime(2024, 3, 25, 11, 7, 0), datetime.datetime(2026, 3, 25, 11, 7, 0))
        pretty_print.pprint(calls)

async def test_get_calls_by_outcome_db():
    async with get_db() as db:
        calls = await get_calls_by_outcome_db(db, "242079fc-0848-4f29-bd3b-698c94860efb","scheduled")
        pretty_print.pprint(calls)

if __name__ == "__main__":
    asyncio.run(test_get_calls_by_outcome_db())

