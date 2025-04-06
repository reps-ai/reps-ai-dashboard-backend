#!/usr/bin/env python3
import sys
import os
import asyncio
import time
import random
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

# Add the parent directory to sys.path to allow importing from backend
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import database connection
from backend.db.connections.database import get_db_session
from sqlalchemy import text

class DatabaseLoadTester:
    def __init__(self):
        self.session = None
        self.leads = []
        self.gyms = []
        self.branches = []
        self.metrics = {
            "queries": 0,
            "start_time": None,
            "end_time": None,
            "errors": 0
        }
    
    async def connect(self):
        """Establish database connection."""
        self.session = await get_db_session()
        print("✅ Connected to database")
        self.metrics["start_time"] = time.time()
    
    async def close(self):
        """Close database connection."""
        if self.session:
            await self.session.close()
            print("✅ Database connection closed")
            self.metrics["end_time"] = time.time()
    
    async def execute_query(self, query, params=None):
        """Execute a SQL query and track metrics."""
        try:
            self.metrics["queries"] += 1
            result = await self.session.execute(text(query), params)
            return result
        except Exception as e:
            self.metrics["errors"] += 1
            print(f"❌ Query error: {str(e)}")
            return None
    
    async def fetch_leads(self, limit=500):
        """Fetch leads from the database."""
        print(f"📊 Fetching up to {limit} leads...")
        query = f"""
        SELECT id, first_name, last_name, phone, email, lead_status, 
               branch_id, gym_id, created_at, source
        FROM leads
        LIMIT {limit}
        """
        result = await self.execute_query(query)
        if result:
            rows = result.fetchall()
            self.leads = [{
                "id": str(row[0]),
                "first_name": row[1],
                "last_name": row[2],
                "phone": row[3],
                "email": row[4],
                "lead_status": row[5],
                "branch_id": str(row[6]) if row[6] else None,
                "gym_id": str(row[7]) if row[7] else None,
                "created_at": row[8],
                "source": row[9]
            } for row in rows]
            print(f"✅ Fetched {len(self.leads)} leads")
            return self.leads
        return []
    
    async def fetch_gyms(self, limit=10):
        """Fetch gyms from the database."""
        print(f"📊 Fetching up to {limit} gyms...")
        query = f"SELECT id, name FROM gyms LIMIT {limit}"
        result = await self.execute_query(query)
        if result:
            rows = result.fetchall()
            self.gyms = [{"id": str(row[0]), "name": row[1]} for row in rows]
            print(f"✅ Fetched {len(self.gyms)} gyms")
            return self.gyms
        return []
    
    async def fetch_branches(self, limit=10):
        """Fetch branches from the database."""
        print(f"📊 Fetching up to {limit} branches...")
        query = f"SELECT id, name FROM branches LIMIT {limit}"
        result = await self.execute_query(query)
        if result:
            rows = result.fetchall()
            self.branches = [{"id": str(row[0]), "name": row[1]} for row in rows]
            print(f"✅ Fetched {len(self.branches)} branches")
            return self.branches
        return []
    
    async def fetch_lead_by_id(self, lead_id):
        """Fetch a single lead by ID."""
        query = "SELECT * FROM leads WHERE id = :lead_id"
        result = await self.execute_query(query, {"lead_id": lead_id})
        if result:
            row = result.fetchone()
            if row:
                columns = result.keys()
                return dict(zip(columns, row))
        return None
    
    async def fetch_leads_by_gym(self, gym_id):
        """Fetch leads by gym ID."""
        query = "SELECT * FROM leads WHERE gym_id = :gym_id LIMIT 50"
        result = await self.execute_query(query, {"gym_id": gym_id})
        if result:
            rows = result.fetchall()
            if rows:
                columns = result.keys()
                return [dict(zip(columns, row)) for row in rows]
        return []
    
    async def fetch_leads_by_branch(self, branch_id):
        """Fetch leads by branch ID."""
        query = "SELECT * FROM leads WHERE branch_id = :branch_id LIMIT 50"
        result = await self.execute_query(query, {"branch_id": branch_id})
        if result:
            rows = result.fetchall()
            if rows:
                columns = result.keys()
                return [dict(zip(columns, row)) for row in rows]
        return []
    
    async def perform_load_test(self, concurrency=20, requests=100):
        """Perform a load test against the database using multiple concurrent queries."""
        # Get initial data first
        await self.fetch_leads()
        await self.fetch_gyms()
        await self.fetch_branches()
        
        if not self.leads:
            print("❌ No leads found, can't perform load test")
            return
        
        print(f"\n🚀 Starting database load test with concurrency={concurrency}, requests={requests}")
        
        # Create a pool of lead IDs, gym IDs, and branch IDs to use
        lead_ids = [lead["id"] for lead in self.leads]
        gym_ids = [gym["id"] for gym in self.gyms] if self.gyms else []
        branch_ids = [branch["id"] for branch in self.branches] if self.branches else []
        
        # Create semaphore to limit concurrency
        semaphore = asyncio.Semaphore(concurrency)
        
        async def _process_request(request_type, item_id):
            """Process a single request with the semaphore."""
            async with semaphore:
                try:
                    if request_type == "lead":
                        result = await self.fetch_lead_by_id(item_id)
                    elif request_type == "gym":
                        result = await self.fetch_leads_by_gym(item_id)
                    elif request_type == "branch":
                        result = await self.fetch_leads_by_branch(item_id)
                    else:
                        return False
                    
                    # Add a small random delay between requests
                    await asyncio.sleep(random.uniform(0.05, 0.2))
                    return result is not None and (
                        isinstance(result, dict) or 
                        (isinstance(result, list) and len(result) > 0)
                    )
                except Exception as e:
                    print(f"❌ Error in _process_request: {str(e)}")
                    return False
        
        # Create a list of requests to make
        requests_to_make = []
        for _ in range(requests):
            request_type = random.choice(["lead", "gym", "branch"] if gym_ids and branch_ids else ["lead"])
            
            if request_type == "lead":
                item_id = random.choice(lead_ids)
            elif request_type == "gym":
                item_id = random.choice(gym_ids)
            else:  # branch
                item_id = random.choice(branch_ids)
            
            requests_to_make.append((request_type, item_id))
        
        # Execute all requests concurrently
        start_time = time.time()
        tasks = [
            asyncio.create_task(_process_request(req_type, item_id)) 
            for req_type, item_id in requests_to_make
        ]
        
        # Show progress indicator
        progress_task = asyncio.create_task(self._show_progress(start_time, len(tasks)))
        
        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks)
        
        # Cancel progress indicator
        progress_task.cancel()
        try:
            await progress_task
        except asyncio.CancelledError:
            pass
        
        # Calculate results
        end_time = time.time()
        total_time = end_time - start_time
        success_count = sum(1 for r in results if r)
        error_count = len(results) - success_count
        
        # Print summary
        print("\n\n📊 Database Load Test Summary:")
        print(f"✅ Successfully executed {success_count} queries")
        print(f"❌ Failed to execute {error_count} queries")
        print(f"⏱️ Total time: {total_time:.2f} seconds")
        print(f"⏱️ Average time per query: {total_time / len(results):.4f} seconds")
        print(f"🔄 Queries per second: {len(results) / total_time:.2f}")
        print(f"📈 Concurrency level: {concurrency}")
        print(f"📊 Total database queries executed: {self.metrics['queries']}")
        print(f"❌ Total database errors: {self.metrics['errors']}")
        
        # Save results to file
        self._save_results_to_file({
            "total_queries": len(results),
            "successful_queries": success_count,
            "failed_queries": error_count,
            "total_time": total_time,
            "avg_time_per_query": total_time / len(results),
            "queries_per_second": len(results) / total_time,
            "concurrency": concurrency,
            "test_date": datetime.now().isoformat()
        })
    
    async def _show_progress(self, start_time, total_tasks):
        """Show a progress indicator."""
        try:
            while True:
                elapsed = time.time() - start_time
                print(f"\rRunning database load test... Elapsed: {elapsed:.1f}s", end="")
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            print("\rProgress tracking cancelled                   ")
            raise
    
    def _save_results_to_file(self, results):
        """Save test results to a file."""
        filename = f"db_load_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, "w") as f:
            f.write("Database Load Test Results\n")
            f.write("==========================\n\n")
            for key, value in results.items():
                f.write(f"{key}: {value}\n")
        print(f"✅ Results saved to {filename}")

async def main():
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Database Load Testing Tool")
    parser.add_argument("--concurrency", type=int, default=20, help="Number of concurrent requests")
    parser.add_argument("--requests", type=int, default=100, help="Total number of requests to make")
    args = parser.parse_args()
    
    # Create the database tester
    tester = DatabaseLoadTester()
    
    try:
        # Connect to the database
        await tester.connect()
        
        # Run the load test
        await tester.perform_load_test(
            concurrency=args.concurrency,
            requests=args.requests
        )
    except Exception as e:
        print(f"❌ Error during test: {str(e)}")
        raise
    finally:
        # Close the database connection
        await tester.close()

if __name__ == "__main__":
    asyncio.run(main()) 