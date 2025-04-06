#!/usr/bin/env python3
import sys
import os
import asyncio
import httpx
import json
import time
from typing import List, Dict, Any, Optional
import uuid
import random
from sqlalchemy import text

# Add the parent directory to sys.path to allow importing from backend
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import our database connection (if needed)
from backend.db.connections.database import get_db_session

# Base URL for the API
BASE_URL = "https://reps-ai-dashboard.rthulabs.com/api"

# Endpoints
ENDPOINTS = {
    "leads": "/leads",
    "lead_by_id": "/leads/{lead_id}",
    "leads_by_gym": "/leads/by-gym/{gym_id}",
    "leads_by_branch": "/leads/by-branch/{branch_id}"
}

# Concurrency settings
MAX_CONCURRENT_REQUESTS = 20
REQUESTS_PER_SECOND = 10  # Target rate limit (can be adjusted)

# API credentials
API_CREDENTIALS = {
    "email": "haha@gmil.com",
    "password": "lollollol"
}

async def get_access_token() -> str:
    """Get access token for API authentication."""
    auth_url = f"{BASE_URL}/auth/login"
    credentials = API_CREDENTIALS
    
    async with httpx.AsyncClient() as client:
        response = await client.post(auth_url, json=credentials)
        if response.status_code == 200:
            data = response.json()
            return data.get("access_token", "")
        else:
            raise Exception(f"Authentication failed: {response.status_code} - {response.text}")

async def fetch_all_leads(token: str) -> List[Dict[Any, Any]]:
    """Fetch all leads from the API."""
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{BASE_URL}{ENDPOINTS['leads']}"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to fetch leads: {response.status_code} - {response.text}")
            return []

async def fetch_lead_by_id(token: str, lead_id: str) -> Optional[Dict[Any, Any]]:
    """Fetch a single lead by its ID."""
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{BASE_URL}{ENDPOINTS['lead_by_id']}".format(lead_id=lead_id)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(url, headers=headers)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to fetch lead {lead_id}: {response.status_code}")
                return None
        except Exception as e:
            print(f"Error fetching lead {lead_id}: {str(e)}")
            return None

async def fetch_leads_by_gym(token: str, gym_id: str) -> List[Dict[Any, Any]]:
    """Fetch leads for a specific gym."""
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{BASE_URL}{ENDPOINTS['leads_by_gym']}".format(gym_id=gym_id)
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to fetch leads for gym {gym_id}: {response.status_code}")
            return []

async def fetch_leads_by_branch(token: str, branch_id: str) -> List[Dict[Any, Any]]:
    """Fetch leads for a specific branch."""
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{BASE_URL}{ENDPOINTS['leads_by_branch']}".format(branch_id=branch_id)
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to fetch leads for branch {branch_id}: {response.status_code}")
            return []

async def get_leads_from_db() -> List[Dict[Any, Any]]:
    """Get lead IDs directly from the database."""
    session = await get_db_session()
    try:
        result = await session.execute(text("SELECT id, first_name, last_name FROM leads LIMIT 300"))
        leads = [{"id": str(row[0]), "first_name": row[1], "last_name": row[2]} for row in result.fetchall()]
        return leads
    finally:
        await session.close()

async def get_gym_branch_ids() -> dict:
    """Get gym and branch IDs from the database."""
    session = await get_db_session()
    try:
        gyms_result = await session.execute(text("SELECT id FROM gyms LIMIT 10"))
        gym_ids = [str(row[0]) for row in gyms_result.fetchall()]
        
        branches_result = await session.execute(text("SELECT id FROM branches LIMIT 10"))
        branch_ids = [str(row[0]) for row in branches_result.fetchall()]
        
        return {
            "gym_ids": gym_ids,
            "branch_ids": branch_ids
        }
    finally:
        await session.close()

async def process_lead(token: str, lead_id: str, semaphore: asyncio.Semaphore) -> bool:
    """Process a single lead with rate limiting via semaphore."""
    async with semaphore:
        result = await fetch_lead_by_id(token, lead_id)
        # Add a small random delay to spread out requests
        await asyncio.sleep(random.uniform(0.05, 0.2))
        return result is not None

async def main():
    # Using hardcoded credentials
    print(f"🚀 Starting API load test against {BASE_URL}")
    
    try:
        # Get authentication token
        token = await get_access_token()
        print(f"✅ Authentication successful")
        
        # Get IDs for gyms and branches
        ids = await get_gym_branch_ids()
        gym_ids = ids.get("gym_ids", [])
        branch_ids = ids.get("branch_ids", [])
        
        print(f"Retrieved {len(gym_ids)} gym IDs and {len(branch_ids)} branch IDs")
        
        # Fetch all leads
        print("📊 Fetching all leads from API...")
        start_time = time.time()
        leads = await fetch_all_leads(token)
        all_leads_time = time.time() - start_time
        
        print(f"✅ Fetched {len(leads)} leads in {all_leads_time:.2f} seconds")
        
        # If API call failed, try getting leads from the database
        if not leads:
            print("⚠️ API call failed, getting leads from database instead...")
            leads = await get_leads_from_db()
            print(f"✅ Retrieved {len(leads)} leads from database")
        
        # Process leads individually with concurrency
        print("\n📝 Fetching individual leads by ID (concurrent)...")
        
        # Create a semaphore to limit concurrency
        semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
        
        # Process up to 100 leads (randomly selected if there are more)
        if len(leads) > 100:
            leads_to_process = random.sample(leads, 100)
        else:
            leads_to_process = leads
        
        start_time = time.time()
        
        # Create tasks for concurrent processing
        tasks = []
        for lead in leads_to_process:
            lead_id = lead.get("id") if isinstance(lead, dict) else str(lead)
            task = asyncio.create_task(process_lead(token, lead_id, semaphore))
            tasks.append(task)
        
        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks)
        
        success_count = sum(1 for r in results if r)
        error_count = sum(1 for r in results if not r)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Also test gym and branch endpoints if IDs are available
        gym_results = []
        branch_results = []
        
        if gym_ids:
            print("\n📊 Testing gym endpoints...")
            for gym_id in gym_ids[:3]:  # Test up to 3 gyms
                result = await fetch_leads_by_gym(token, gym_id)
                gym_results.append(len(result) if result else 0)
        
        if branch_ids:
            print("\n📊 Testing branch endpoints...")
            for branch_id in branch_ids[:3]:  # Test up to 3 branches
                result = await fetch_leads_by_branch(token, branch_id)
                branch_results.append(len(result) if result else 0)
        
        # Print summary
        print("\n📊 API Load Test Summary:")
        print(f"✅ Successfully fetched {success_count} individual leads")
        print(f"❌ Failed to fetch {error_count} leads")
        print(f"⏱️ Total time for concurrent individual requests: {total_time:.2f} seconds")
        print(f"⏱️ Average time per lead: {total_time / len(leads_to_process):.2f} seconds")
        print(f"🔄 Requests per second: {len(leads_to_process) / total_time:.2f}")
        print(f"📈 Concurrency level: {MAX_CONCURRENT_REQUESTS}")
        
        if gym_results:
            print(f"🏢 Gym endpoint test: fetched {sum(gym_results)} leads across {len(gym_results)} gyms")
        
        if branch_results:
            print(f"🏢 Branch endpoint test: fetched {sum(branch_results)} leads across {len(branch_results)} branches")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main()) 