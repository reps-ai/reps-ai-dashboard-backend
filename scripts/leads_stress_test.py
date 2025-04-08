#!/usr/bin/env python3
import sys
import os
import asyncio
import httpx
import time
import random
import uuid
import json
from datetime import datetime

# Add the parent directory to sys.path to allow importing from backend
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import our database connection
from backend.db.connections.database import get_db_session
from sqlalchemy import text

# API authentication
BEARER_TOKEN = os.environ.get("BEARER_TOKEN")
if not BEARER_TOKEN:
    print("⚠️ Warning: BEARER_TOKEN environment variable not set.")
    print("Please set it with: export BEARER_TOKEN='Bearer your-token-here'")
    sys.exit(1)

# Base URL for the API
BASE_URL = "https://reps-ai-backend.rthulabs.com/api"

# Branch ID to use for leads
TARGET_BRANCH_ID = "e3bff29b-a204-46f5-be4d-f14bf3e69c41"

# API endpoints
LEADS_ENDPOINT = "/leads/"
LEAD_BY_ID_ENDPOINT = "/leads/{id}/"

# Stress test configuration
DEFAULT_CONCURRENCY = 100
DEFAULT_REQUESTS = 1000
DEFAULT_DURATION = 60  # seconds
TIMEOUT = 30.0  # seconds for request timeout

# Add logging capability
def log_api_response(response_type, response_text, status_code, details=None):
    """Write API response data to a log file for inspection"""
    log_file = "api_response_log.txt"
    timestamp = datetime.now().isoformat()
    
    with open(log_file, "a") as f:
        f.write(f"\n\n===== {timestamp} - {response_type} (Status: {status_code}) =====\n")
        if details:
            f.write(f"Details: {json.dumps(details, default=str)}\n")
        f.write(f"Response: {response_text[:2000]}")  # Limit to prevent huge files
        f.write("\n" + "=" * 80 + "\n")
    
    print(f"📝 Logged {response_type} response to {log_file}")

class LeadStressTester:
    def __init__(self, concurrency=DEFAULT_CONCURRENCY, branch_id=TARGET_BRANCH_ID):
        self.concurrency = concurrency
        self.branch_id = branch_id
        self.semaphore = asyncio.Semaphore(concurrency)
        self.results = {
            "all_leads_requests": 0,
            "all_leads_successful": 0,
            "all_leads_failed": 0,
            "lead_by_id_requests": 0,
            "lead_by_id_successful": 0,
            "lead_by_id_failed": 0,
            "timeouts": 0,
            "start_time": None,
            "end_time": None
        }
        self.lead_ids = []
        self.db_session = None
        # Set headers with bearer token
        self.headers = {"Authorization": BEARER_TOKEN}
        
    async def connect_to_db(self):
        """Connect to the MCP database."""
        print("🔌 Connecting to database via MCP...")
        try:
            self.db_session = await get_db_session()
            print("✅ Connected to database")
            return True
        except Exception as e:
            print(f"❌ Error connecting to database: {str(e)}")
            return False
            
    async def get_leads_from_db(self, limit=100):
        """Get real lead IDs from the database for a specific branch."""
        if not self.db_session:
            print("❌ Not connected to database")
            return []
            
        print(f"🔍 Getting leads from database for branch: {self.branch_id}")
        try:
            query = """
            SELECT id, first_name, last_name
            FROM leads
            WHERE branch_id = :branch_id
            LIMIT :limit
            """
            
            result = await self.db_session.execute(
                text(query), 
                {"branch_id": self.branch_id, "limit": limit}
            )
            
            rows = result.fetchall()
            leads = [{"id": str(row[0]), "name": f"{row[1]} {row[2]}"} for row in rows]
            
            print(f"✅ Retrieved {len(leads)} leads from database")
            return leads
        except Exception as e:
            print(f"❌ Error getting leads from database: {str(e)}")
            return []
            
    async def close_db_connection(self):
        """Close the database connection."""
        if self.db_session:
            try:
                await self.db_session.close()
                print("✅ Database connection closed")
            except Exception as e:
                print(f"❌ Error closing database connection: {str(e)}")
        
    async def discover_lead_ids(self):
        """Get real lead IDs from the database or API, or use fallback random UUIDs."""
        # First try getting leads from database
        if await self.connect_to_db():
            db_leads = await self.get_leads_from_db(limit=200)
            if db_leads:
                self.lead_ids = [lead["id"] for lead in db_leads]
                print(f"✅ Using {len(self.lead_ids)} real lead IDs from database")
                await self.close_db_connection()
                return
            await self.close_db_connection()
        
        # If database method fails, try API
        print("🔍 Attempting to discover lead IDs from API...")
        try:
            async with httpx.AsyncClient(timeout=TIMEOUT) as client:
                response = await client.get(f"{BASE_URL}/leads")
                if response.status_code == 200:
                    leads = response.json()
                    if isinstance(leads, list) and leads:
                        self.lead_ids = [lead.get("id") for lead in leads if lead.get("id")]
                        print(f"✅ Found {len(self.lead_ids)} real lead IDs from API")
                        return
        except Exception as e:
            print(f"❌ Error discovering lead IDs from API: {str(e)}")
        
        # If all methods fail, create random ones
        self.lead_ids = [str(uuid.uuid4()) for _ in range(20)]
        print(f"⚠️ Using {len(self.lead_ids)} fallback random UUIDs for leads")
    
    async def request_all_leads(self):
        """Make a request to get all leads."""
        async with self.semaphore:
            self.results["all_leads_requests"] += 1
            url = f"{BASE_URL}{LEADS_ENDPOINT}"
            
            try:
                async with httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=True) as client:
                    response = await client.get(url, headers=self.headers)
                    
                    # Add small random delay to avoid overwhelming
                    await asyncio.sleep(random.uniform(0.01, 0.05))
                    
                    if response.status_code < 400:
                        self.results["all_leads_successful"] += 1
                        
                        # Log a sample of the responses for verification
                        if self.results["all_leads_successful"] <= 2:  # Log only first 2
                            try:
                                # Log raw response text instead of parsing JSON
                                log_api_response(
                                    "all_leads", 
                                    response.text, 
                                    response.status_code,
                                    {"url": url}
                                )
                                
                                # Try to parse JSON for lead IDs
                                leads = response.json()
                                if isinstance(leads, dict) and "data" in leads:
                                    leads_data = leads["data"]
                                    new_ids = [lead.get("id") for lead in leads_data if lead.get("id")]
                                    if new_ids:
                                        self.lead_ids = new_ids
                                        print(f"Updated lead IDs from API, found {len(new_ids)} leads")
                            except Exception as e:
                                print(f"Error processing all_leads response: {str(e)}")
                        
                        return True
                    else:
                        self.results["all_leads_failed"] += 1
                        if random.random() < 0.05:  # Only show ~5% of errors
                            print(f"❌ All leads request failed: {response.status_code} - {response.text if len(response.text) < 100 else response.text[:100]+'...'}")
                        return False
            except httpx.TimeoutException:
                self.results["timeouts"] += 1
                if random.random() < 0.05:
                    print(f"⏱️ All leads request timeout")
                return False
            except Exception as e:
                self.results["all_leads_failed"] += 1
                if random.random() < 0.05:
                    print(f"❌ All leads request error: {str(e)}")
                return False
    
    async def request_lead_by_id(self, lead_id):
        """Make a request to get a specific lead by ID."""
        async with self.semaphore:
            self.results["lead_by_id_requests"] += 1
            url = f"{BASE_URL}{LEAD_BY_ID_ENDPOINT.format(id=lead_id)}"
            
            try:
                async with httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=True) as client:
                    response = await client.get(url, headers=self.headers)
                    
                    # Add small random delay to avoid overwhelming
                    await asyncio.sleep(random.uniform(0.01, 0.05))
                    
                    if response.status_code < 400:
                        self.results["lead_by_id_successful"] += 1
                        
                        # Log a sample of the responses for verification
                        if self.results["lead_by_id_successful"] <= 2:  # Log only first 2
                            try:
                                # Log raw response text instead of parsing JSON
                                log_api_response(
                                    "lead_by_id", 
                                    response.text, 
                                    response.status_code,
                                    {"url": url, "lead_id": lead_id}
                                )
                            except Exception as e:
                                print(f"❌ Error logging lead response: {str(e)}")
                        
                        return True
                    else:
                        self.results["lead_by_id_failed"] += 1
                        if random.random() < 0.05:  # Only show ~5% of errors
                            print(f"❌ Lead by ID request failed for ID {lead_id}: {response.status_code} - {response.text if len(response.text) < 100 else response.text[:100]+'...'}")
                        return False
            except httpx.TimeoutException:
                self.results["timeouts"] += 1
                if random.random() < 0.05:
                    print(f"⏱️ Lead by ID request timeout for ID {lead_id}")
                return False
            except Exception as e:
                self.results["lead_by_id_failed"] += 1
                if random.random() < 0.05:
                    print(f"❌ Lead by ID request error for ID {lead_id}: {str(e)}")
                return False
    
    async def run_stress_test(self, duration_seconds):
        """Run stress test hitting leads endpoints for specified duration."""
        print(f"\n🚀 Starting leads API stress test for {duration_seconds} seconds with concurrency {self.concurrency}")
        self.results["start_time"] = time.time()
        end_time = self.results["start_time"] + duration_seconds
        
        # Track total tasks created
        total_tasks = 0
        tasks = []
        
        # Show progress indicator
        progress_task = asyncio.create_task(self._show_progress(duration_seconds))
        
        # Keep creating and executing tasks until the time is up
        while time.time() < end_time:
            # Create a new batch of tasks
            batch_size = self.concurrency * 2  # Create twice as many tasks as concurrency
            for _ in range(batch_size):
                # 40% chance of getting all leads, 60% chance of getting lead by ID
                if random.random() < 0.4:
                    task = asyncio.create_task(self.request_all_leads())
                else:
                    # Get a random lead ID
                    lead_id = random.choice(self.lead_ids)
                    task = asyncio.create_task(self.request_lead_by_id(lead_id))
                
                tasks.append(task)
                total_tasks += 1
            
            # Wait for this batch to complete
            await asyncio.gather(*tasks)
            tasks = []
            
            # Check if we're out of time
            if time.time() >= end_time:
                break
        
        # Cancel progress indicator
        progress_task.cancel()
        try:
            await progress_task
        except asyncio.CancelledError:
            pass
        
        self.results["end_time"] = time.time()
        
        # Print final results
        print(f"\nCompleted {total_tasks} total requests during {duration_seconds} second test")
        self._print_summary()
    
    async def _show_progress(self, total_duration):
        """Show a progress indicator for the running test."""
        try:
            while True:
                elapsed = time.time() - self.results["start_time"]
                percent = min(100, (elapsed / total_duration) * 100)
                remaining = max(0, total_duration - elapsed)
                
                all_leads = self.results["all_leads_successful"] + self.results["all_leads_failed"]
                lead_by_id = self.results["lead_by_id_successful"] + self.results["lead_by_id_failed"]
                total = all_leads + lead_by_id
                
                rps = total / elapsed if elapsed > 0 else 0
                
                print(f"\rProgress: {elapsed:.1f}s/{total_duration}s ({percent:.1f}%) | "
                      f"Requests: {total} | RPS: {rps:.1f} | "
                      f"All leads: {all_leads} | Lead by ID: {lead_by_id}", end="")
                
                await asyncio.sleep(0.5)
        except asyncio.CancelledError:
            print("\r" + " " * 100, end="\n")  # Clear the line
            raise
    
    def _print_summary(self):
        """Print a summary of test results."""
        total_time = self.results["end_time"] - self.results["start_time"]
        
        all_leads_total = self.results["all_leads_successful"] + self.results["all_leads_failed"]
        lead_by_id_total = self.results["lead_by_id_successful"] + self.results["lead_by_id_failed"]
        total_requests = all_leads_total + lead_by_id_total
        
        print("\n\n📊 Leads API Stress Test Summary:")
        print("====================================")
        
        print("\n🔍 All Leads Endpoint:")
        if all_leads_total > 0:
            print(f"  ✅ Successful: {self.results['all_leads_successful']} ({(self.results['all_leads_successful']/all_leads_total)*100:.1f}%)")
            print(f"  ❌ Failed: {self.results['all_leads_failed']} ({(self.results['all_leads_failed']/all_leads_total)*100:.1f}%)")
        else:
            print(f"  ✅ Successful: 0 (0.0%)")
            print(f"  ❌ Failed: 0 (0.0%)")
        
        print("\n🔍 Lead by ID Endpoint:")
        if lead_by_id_total > 0:
            print(f"  ✅ Successful: {self.results['lead_by_id_successful']} ({(self.results['lead_by_id_successful']/lead_by_id_total)*100:.1f}%)")
            print(f"  ❌ Failed: {self.results['lead_by_id_failed']} ({(self.results['lead_by_id_failed']/lead_by_id_total)*100:.1f}%)")
        else:
            print(f"  ✅ Successful: 0 (0.0%)")
            print(f"  ❌ Failed: 0 (0.0%)")
        
        print(f"\n⏱️ Timeouts: {self.results['timeouts']}")
        print(f"⏱️ Total test duration: {total_time:.2f} seconds")
        print(f"🔄 Requests per second: {total_requests/total_time:.2f}")
        print(f"📈 Concurrency level: {self.concurrency}")
        
        # Save results to file
        self._save_results()
    
    def _save_results(self):
        """Save test results to a file."""
        filename = f"leads_stress_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(filename, "w") as f:
            f.write("Leads API Stress Test Results\n")
            f.write("===========================\n\n")
            
            total_time = self.results["end_time"] - self.results["start_time"]
            
            all_leads_total = self.results["all_leads_successful"] + self.results["all_leads_failed"]
            lead_by_id_total = self.results["lead_by_id_successful"] + self.results["lead_by_id_failed"]
            total_requests = all_leads_total + lead_by_id_total
            
            f.write(f"Test Date: {datetime.now().isoformat()}\n")
            f.write(f"Target API: {BASE_URL}\n\n")
            
            f.write("All Leads Endpoint:\n")
            f.write(f"  Total Requests: {all_leads_total}\n")
            if all_leads_total > 0:
                f.write(f"  Successful: {self.results['all_leads_successful']} ({(self.results['all_leads_successful']/all_leads_total)*100:.1f}%)\n")
                f.write(f"  Failed: {self.results['all_leads_failed']} ({(self.results['all_leads_failed']/all_leads_total)*100:.1f}%)\n\n")
            else:
                f.write("  Successful: 0 (0.0%)\n")
                f.write("  Failed: 0 (0.0%)\n\n")
            
            f.write("Lead by ID Endpoint:\n")
            f.write(f"  Total Requests: {lead_by_id_total}\n")
            if lead_by_id_total > 0:
                f.write(f"  Successful: {self.results['lead_by_id_successful']} ({(self.results['lead_by_id_successful']/lead_by_id_total)*100:.1f}%)\n")
                f.write(f"  Failed: {self.results['lead_by_id_failed']} ({(self.results['lead_by_id_failed']/lead_by_id_total)*100:.1f}%)\n\n")
            else:
                f.write("  Successful: 0 (0.0%)\n")
                f.write("  Failed: 0 (0.0%)\n\n")
            
            f.write(f"Timeouts: {self.results['timeouts']}\n")
            f.write(f"Total Test Duration: {total_time:.2f} seconds\n")
            f.write(f"Requests Per Second: {total_requests/total_time:.2f}\n")
            f.write(f"Concurrency Level: {self.concurrency}\n")
        
        print(f"✅ Results saved to {filename}")

async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Leads API Stress Testing Tool")
    parser.add_argument("--concurrency", type=int, default=DEFAULT_CONCURRENCY, 
                        help=f"Number of concurrent requests (default: {DEFAULT_CONCURRENCY})")
    parser.add_argument("--duration", type=int, default=DEFAULT_DURATION,
                       help=f"Duration of the test in seconds (default: {DEFAULT_DURATION})")
    
    args = parser.parse_args()
    
    # Create stress tester
    tester = LeadStressTester(concurrency=args.concurrency)
    
    # Try to discover lead IDs
    await tester.discover_lead_ids()
    
    # Run the stress test
    await tester.run_stress_test(args.duration)

if __name__ == "__main__":
    asyncio.run(main()) 