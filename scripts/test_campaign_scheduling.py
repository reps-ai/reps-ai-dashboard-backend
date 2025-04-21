"""
Script to test campaign call scheduling functionality directly.
"""
import asyncio
import os
import sys
from datetime import datetime, date, timedelta
import uuid
from contextlib import asynccontextmanager

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.db.connections.database import get_db
from backend.tasks.campaign.schedule_calls import schedule_calls_for_campaign, schedule_calls_for_all_campaigns
from backend.db.repositories.campaign import create_campaign_repository
from backend.db.models.campaign.follow_up_campaign import FollowUpCampaign
from backend.db.models.gym.branch import Branch
from backend.db.models.gym.gym import Gym
from sqlalchemy import select, and_, join

# Create an async context manager to properly use the get_db generator
@asynccontextmanager
async def db_session():
    """
    Context manager to properly handle the database session.
    """
    db_gen = get_db()
    try:
        session = await db_gen.__anext__()
        yield session
    finally:
        try:
            await db_gen.__anext__()
        except StopAsyncIteration:
            pass

async def list_gyms_and_branches():
    """List all gyms and their branches."""
    print("\nAvailable Gyms and Branches:")
    print("===========================")
    
    async with db_session() as session:
        # Query all gyms
        gyms_query = select(Gym)
        gyms_result = await session.execute(gyms_query)
        gyms = gyms_result.scalars().all()
        
        for gym in gyms:
            print(f"\nGym: {gym.name} (ID: {gym.id})")
            
            # Query branches for this gym
            branches_query = select(Branch).where(Branch.gym_id == gym.id)
            branches_result = await session.execute(branches_query)
            branches = branches_result.scalars().all()
            
            for branch in branches:
                print(f"  - Branch: {branch.name} (ID: {branch.id})")
                
                # Count campaigns for this branch
                campaigns_query = select(FollowUpCampaign).where(FollowUpCampaign.branch_id == branch.id)
                campaigns_result = await session.execute(campaigns_query)
                campaigns = campaigns_result.scalars().all()
                
                print(f"    Campaigns: {len(campaigns)}")

async def create_test_campaign():
    """Create a test campaign with a lead for testing."""
    print("\nCreating Test Campaign:")
    print("=====================")
    
    async with db_session() as session:
        # First list branches to choose from
        branches_query = select(Branch)
        branches_result = await session.execute(branches_query)
        branches = branches_result.scalars().all()
        
        print("\nSelect a branch for the test campaign:")
        for i, branch in enumerate(branches):
            print(f"{i+1}. {branch.name} (ID: {branch.id})")
            
        branch_idx = int(input("\nSelect a branch (number): ")) - 1
        if branch_idx < 0 or branch_idx >= len(branches):
            print("Invalid selection")
            return
            
        branch = branches[branch_idx]
        
        # Create a campaign
        campaign_id = uuid.uuid4()
        start_date = datetime.now() - timedelta(days=1)
        end_date = datetime.now() + timedelta(days=30)
        
        campaign = FollowUpCampaign(
            id=campaign_id,
            branch_id=branch.id,
            gym_id=branch.gym_id,
            name=f"Test Campaign {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            description="Campaign created for testing",
            start_date=start_date,
            end_date=end_date,
            frequency=10,
            gap=1,
            campaign_status="active",
            call_count=0,
            metrics={"created_by": "test_script"}
        )
        
        session.add(campaign)
        await session.commit()
        
        print(f"\nCreated test campaign: {campaign.name} (ID: {campaign.id})")
        print(f"Branch: {branch.name} (ID: {branch.id})")
        
        # Now fetch leads for the branch to add to the campaign
        from backend.db.models.lead.lead import Lead
        leads_query = select(Lead).where(Lead.branch_id == branch.id).limit(3)
        leads_result = await session.execute(leads_query)
        leads = leads_result.scalars().all()
        
        if not leads:
            print("No leads found for this branch. Campaign created but without leads.")
            return
        
        # Update the leads to include the campaign
        for lead in leads:
            lead.campaign_id = campaign_id
            
        await session.commit()
        print(f"Added {len(leads)} leads to the campaign")
        
        return str(campaign_id)

async def test_schedule_campaign_calls():
    """Test scheduling calls for a specific campaign."""
    print("\nTesting Campaign Call Scheduling:")
    print("===============================")
    
    async with db_session() as session:
        # Option to list all branches
        list_branches = input("List all gyms and branches first? (y/n): ").lower() == 'y'
        if list_branches:
            await list_gyms_and_branches()
            
        # Option to create a test campaign
        create_campaign = input("\nCreate a test campaign first? (y/n): ").lower() == 'y'
        if create_campaign:
            campaign_id = await create_test_campaign()
            if campaign_id:
                use_new_campaign = input("\nUse the newly created campaign for testing? (y/n): ").lower() == 'y'
                if use_new_campaign:
                    # Get the campaign and schedule calls
                    campaign_repo = await create_campaign_repository(session)
                    campaign = await campaign_repo.get_campaign_by_id(campaign_id)
                    
                    print(f"\nTesting with campaign: {campaign['name']} (ID: {campaign_id})")
                    
                    # Schedule calls for today
                    today = date.today()
                    scheduled_calls = await schedule_calls_for_campaign(campaign_id, today)
                    
                    print(f"Scheduled {len(scheduled_calls)} calls for today:")
                    for call in scheduled_calls:
                        print(f"  - Lead: {call['lead_id']}, Time: {call['scheduled_time']}")
                    
                    # Get the updated campaign to verify call count was incremented
                    updated_campaign = await campaign_repo.get_campaign_by_id(campaign_id)
                    print(f"Campaign call count is now: {updated_campaign['call_count']}")
                    
                    return
        
        # Get a branch ID to test with
        branch_id = input("\nEnter a branch ID to test with (or press Enter to list branches): ")
        if not branch_id:
            # List branches and let user select one
            branches_query = select(Branch)
            branches_result = await session.execute(branches_query)
            branches = branches_result.scalars().all()
            
            print("\nAvailable branches:")
            for i, branch in enumerate(branches):
                print(f"{i+1}. {branch.name} (ID: {branch.id})")
                
            branch_idx = int(input("\nSelect a branch (number): ")) - 1
            if branch_idx < 0 or branch_idx >= len(branches):
                print("Invalid selection")
                return
                
            branch_id = str(branches[branch_idx].id)
        
        # Get campaigns directly from database for the branch
        try:
            # Convert branch_id to UUID
            branch_uuid = uuid.UUID(branch_id)
            
            # Directly query the campaigns for this branch
            query = select(FollowUpCampaign).where(FollowUpCampaign.branch_id == branch_uuid)
            result = await session.execute(query)
            campaigns = result.scalars().all()
            
            if not campaigns:
                print(f"No campaigns found for branch ID: {branch_id}")
                
                # Offer to create a test campaign
                create_test = input("Would you like to create a test campaign for this branch? (y/n): ").lower() == 'y'
                if create_test:
                    # Get the branch info
                    branch_query = select(Branch).where(Branch.id == branch_uuid)
                    branch_result = await session.execute(branch_query)
                    branch = branch_result.scalar_one_or_none()
                    
                    if not branch:
                        print("Branch not found.")
                        return
                    
                    # Create a campaign
                    campaign_id = uuid.uuid4()
                    start_date = datetime.now() - timedelta(days=1)
                    end_date = datetime.now() + timedelta(days=30)
                    
                    campaign = FollowUpCampaign(
                        id=campaign_id,
                        branch_id=branch.id,
                        gym_id=branch.gym_id,
                        name=f"Test Campaign {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                        description="Campaign created for testing",
                        start_date=start_date,
                        end_date=end_date,
                        frequency=10,
                        gap=1,
                        campaign_status="active",
                        call_count=0,
                        metrics={"created_by": "test_script"}
                    )
                    
                    session.add(campaign)
                    await session.commit()
                    
                    print(f"\nCreated test campaign: {campaign.name} (ID: {campaign.id})")
                    
                    # Now fetch leads for the branch to add to the campaign
                    from backend.db.models.lead.lead import Lead
                    leads_query = select(Lead).where(Lead.branch_id == branch.id).limit(3)
                    leads_result = await session.execute(leads_query)
                    leads = leads_result.scalars().all()
                    
                    if not leads:
                        print("No leads found for this branch. Creating test campaign but it can't be tested without leads.")
                        return
                    
                    # Update the leads to include the campaign
                    for lead in leads:
                        lead.campaign_id = campaign_id
                        
                    await session.commit()
                    print(f"Added {len(leads)} leads to the campaign")
                    
                    # Schedule calls for the new campaign
                    print(f"\nTesting with new campaign: {campaign.name} (ID: {campaign_id})")
                    
                    # Schedule calls for today
                    today = date.today()
                    scheduled_calls = await schedule_calls_for_campaign(str(campaign_id), today)
                    
                    print(f"Scheduled {len(scheduled_calls)} calls for today:")
                    for call in scheduled_calls:
                        print(f"  - Lead: {call['lead_id']}, Time: {call['scheduled_time']}")
                    
                    # Get the updated campaign to verify call count was incremented
                    campaign_repo = await create_campaign_repository(session)
                    updated_campaign = await campaign_repo.get_campaign_by_id(str(campaign_id))
                    print(f"Campaign call count is now: {updated_campaign['call_count']}")
                
                return
            
            # Convert campaigns to dictionaries for display
            campaign_dicts = [campaign.to_dict() for campaign in campaigns]
            
            print("\nAvailable campaigns:")
            for i, campaign in enumerate(campaign_dicts):
                print(f"{i+1}. {campaign['name']} (ID: {campaign['id']})")
                
            campaign_idx = int(input("\nSelect a campaign (number): ")) - 1
            if campaign_idx < 0 or campaign_idx >= len(campaign_dicts):
                print("Invalid selection")
                return
                
            campaign_id = str(campaign_dicts[campaign_idx]["id"])
            print(f"Testing with campaign: {campaign_dicts[campaign_idx]['name']} (ID: {campaign_id})")
            
            # Schedule calls for today
            today = date.today()
            scheduled_calls = await schedule_calls_for_campaign(campaign_id, today)
            
            print(f"Scheduled {len(scheduled_calls)} calls for today:")
            for call in scheduled_calls:
                print(f"  - Lead: {call['lead_id']}, Time: {call['scheduled_time']}")
            
            # Get the updated campaign to verify call count was incremented
            campaign_repo = await create_campaign_repository(session)
            updated_campaign = await campaign_repo.get_campaign_by_id(campaign_id)
            print(f"Campaign call count is now: {updated_campaign['call_count']}")
            
        except ValueError as e:
            print(f"Error: {str(e)}")
        except Exception as e:
            print(f"Unexpected error: {str(e)}")


async def test_schedule_all_campaigns():
    """Test scheduling calls for all active campaigns."""
    print("\nTesting scheduling for all campaigns...")
    
    # Schedule calls for all campaigns
    today = date.today()
    results = await schedule_calls_for_all_campaigns(today)
    
    print(f"Scheduled calls for {len(results)} campaigns:")
    for campaign_id, calls in results.items():
        print(f"  - Campaign {campaign_id}: {len(calls)} calls scheduled")


async def main():
    """Run all tests."""
    print("Campaign Call Scheduling Test")
    print("===========================")
    
    while True:
        print("\nSelect a test:")
        print("1. Test specific campaign")
        print("2. Test all campaigns")
        print("3. Exit")
        
        choice = input("Your choice: ")
        
        if choice == "1":
            await test_schedule_campaign_calls()
        elif choice == "2":
            await test_schedule_all_campaigns()
        elif choice == "3":
            break
        else:
            print("Invalid choice")


if __name__ == "__main__":
    asyncio.run(main())
