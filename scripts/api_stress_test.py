#!/usr/bin/env python3
import sys
import os
import asyncio
import httpx
import json
import time
import random
from datetime import datetime
from typing import List, Dict, Any, Optional
import uuid

# Base URL for the API
BASE_URL = "https://reps-ai-dashboard.rthulabs.com/api"

# List of endpoints to hit
ENDPOINTS = [
    "/leads",
    "/leads/count",
    "/leads/stats",
    "/gyms",
    "/branches",
    "/users",
    "/gym-settings",
    "/voice-settings",
    "/ai-settings",
    "/call-settings",
    "/knowledge-base"
]

# Specific ID endpoints (will be dynamically populated)
ID_ENDPOINTS = {
    "lead": "/leads/{id}",
    "gym": "/gyms/{id}",
    "branch": "/branches/{id}",
    "user": "/users/{id}",
}

# Stress test configuration
DEFAULT_CONCURRENCY = 50
DEFAULT_REQUESTS = 1000
DEFAULT_DURATION = 60  # seconds
TIMEOUT = 30.0  # seconds for request timeout

class APIStressTester:
    def __init__(self, concurrency=DEFAULT_CONCURRENCY):
        self.concurrency = concurrency
        self.semaphore = asyncio.Semaphore(concurrency)
        self.results = {
            "requests": 0,
            "successful": 0,
            "failed": 0,
            "timeouts": 0,
            "start_time": None,
            "end_time": None
        }
        self.ids = {
            "lead": [],
            "gym": [],
            "branch": [],
            "user": []
        }
        self.headers = {}
    
    async def discover_ids(self):
        """Discover IDs from the API for various entities."""
        print("🔍 Discovering entity IDs...")
        
        # Try to get lead IDs
        try:
            async with httpx.AsyncClient(timeout=TIMEOUT) as client:
                response = await client.get(f"{BASE_URL}/leads", headers=self.headers)
                if response.status_code == 200:
                    leads = response.json()
                    self.ids["lead"] = [lead.get("id") for lead in leads if lead.get("id")]
                    print(f"✅ Found {len(self.ids['lead'])} lead IDs")
        except Exception as e:
            print(f"❌ Error discovering lead IDs: {str(e)}")
        
        # Try to get gym IDs
        try:
            async with httpx.AsyncClient(timeout=TIMEOUT) as client:
                response = await client.get(f"{BASE_URL}/gyms", headers=self.headers)
                if response.status_code == 200:
                    gyms = response.json()
                    self.ids["gym"] = [gym.get("id") for gym in gyms if gym.get("id")]
                    print(f"✅ Found {len(self.ids['gym'])} gym IDs")
        except Exception as e:
            print(f"❌ Error discovering gym IDs: {str(e)}")
        
        # Try to get branch IDs
        try:
            async with httpx.AsyncClient(timeout=TIMEOUT) as client:
                response = await client.get(f"{BASE_URL}/branches", headers=self.headers)
                if response.status_code == 200:
                    branches = response.json()
                    self.ids["branch"] = [branch.get("id") for branch in branches if branch.get("id")]
                    print(f"✅ Found {len(self.ids['branch'])} branch IDs")
        except Exception as e:
            print(f"❌ Error discovering branch IDs: {str(e)}")
        
        # Try to get user IDs
        try:
            async with httpx.AsyncClient(timeout=TIMEOUT) as client:
                response = await client.get(f"{BASE_URL}/users", headers=self.headers)
                if response.status_code == 200:
                    users = response.json()
                    self.ids["user"] = [user.get("id") for user in users if user.get("id")]
                    print(f"✅ Found {len(self.ids['user'])} user IDs")
        except Exception as e:
            print(f"❌ Error discovering user IDs: {str(e)}")
        
        # If we couldn't find any IDs, add some placeholder UUIDs
        for key in self.ids:
            if not self.ids[key]:
                # Add some random UUIDs as fallback
                self.ids[key] = [str(uuid.uuid4()) for _ in range(5)]
                print(f"⚠️ Using fallback random UUIDs for {key}")
    
    async def make_request(self, endpoint: str, is_id_endpoint=False, entity_type=None, entity_id=None):
        """Make a single API request with rate limiting."""
        async with self.semaphore:
            self.results["requests"] += 1
            
            # Prepare the URL
            if is_id_endpoint:
                url = f"{BASE_URL}{ID_ENDPOINTS[entity_type].format(id=entity_id)}"
            else:
                url = f"{BASE_URL}{endpoint}"
            
            try:
                async with httpx.AsyncClient(timeout=TIMEOUT) as client:
                    response = await client.get(url, headers=self.headers)
                    
                    # Add small random delay between requests
                    await asyncio.sleep(random.uniform(0.01, 0.1))
                    
                    if response.status_code < 400:  # Consider any non-4xx/5xx as success
                        self.results["successful"] += 1
                        return True
                    else:
                        self.results["failed"] += 1
                        # Print only some of the errors to avoid flooding the console
                        if random.random() < 0.05:  # Only show ~5% of errors
                            print(f"❌ Request failed: {url} - {response.status_code}")
                        return False
            except httpx.TimeoutException:
                self.results["timeouts"] += 1
                # Print only some of the timeouts to avoid flooding the console
                if random.random() < 0.05:  # Only show ~5% of timeouts
                    print(f"⏱️ Request timeout: {url}")
                return False
            except Exception as e:
                self.results["failed"] += 1
                # Print only some of the errors to avoid flooding the console
                if random.random() < 0.05:  # Only show ~5% of errors
                    print(f"❌ Request error: {url} - {str(e)}")
                return False
    
    async def run_requests(self, num_requests):
        """Run a specific number of requests."""
        print(f"\n🚀 Starting stress test with {num_requests} requests at concurrency {self.concurrency}")
        self.results["start_time"] = time.time()
        
        # Create tasks list
        tasks = []
        
        # Mix regular endpoints and ID-specific endpoints
        for _ in range(num_requests):
            # 70% chance of hitting a regular endpoint, 30% chance of hitting an ID endpoint
            if random.random() < 0.7:
                endpoint = random.choice(ENDPOINTS)
                task = asyncio.create_task(self.make_request(endpoint))
            else:
                entity_type = random.choice(list(self.ids.keys()))
                if self.ids[entity_type]:
                    entity_id = random.choice(self.ids[entity_type])
                    task = asyncio.create_task(
                        self.make_request(None, True, entity_type, entity_id)
                    )
                else:
                    # Fallback to regular endpoint if no IDs available
                    endpoint = random.choice(ENDPOINTS)
                    task = asyncio.create_task(self.make_request(endpoint))
            
            tasks.append(task)
        
        # Show progress indicator
        progress_task = asyncio.create_task(self._show_progress(num_requests))
        
        # Wait for all tasks to complete
        await asyncio.gather(*tasks)
        
        # Cancel progress indicator
        progress_task.cancel()
        try:
            await progress_task
        except asyncio.CancelledError:
            pass
        
        self.results["end_time"] = time.time()
        
        # Print summary
        self._print_summary()
    
    async def run_for_duration(self, duration_seconds):
        """Run requests continuously for a specified duration."""
        print(f"\n🚀 Starting stress test for {duration_seconds} seconds at concurrency {self.concurrency}")
        self.results["start_time"] = time.time()
        end_time = self.results["start_time"] + duration_seconds
        
        # Track total tasks created
        total_tasks = 0
        tasks = []
        
        # Show progress indicator
        progress_task = asyncio.create_task(self._show_duration_progress(duration_seconds))
        
        # Keep creating and executing tasks until the time is up
        while time.time() < end_time:
            # Create a new batch of tasks
            batch_size = self.concurrency * 2  # Create twice as many tasks as concurrency
            for _ in range(batch_size):
                # 70% chance of hitting a regular endpoint, 30% chance of hitting an ID endpoint
                if random.random() < 0.7:
                    endpoint = random.choice(ENDPOINTS)
                    task = asyncio.create_task(self.make_request(endpoint))
                else:
                    entity_type = random.choice(list(self.ids.keys()))
                    if self.ids[entity_type]:
                        entity_id = random.choice(self.ids[entity_type])
                        task = asyncio.create_task(
                            self.make_request(None, True, entity_type, entity_id)
                        )
                    else:
                        # Fallback to regular endpoint if no IDs available
                        endpoint = random.choice(ENDPOINTS)
                        task = asyncio.create_task(self.make_request(endpoint))
                
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
        
        # Print summary
        print(f"\nCompleted {total_tasks} total requests during test duration")
        self._print_summary()
    
    async def _show_progress(self, total_requests):
        """Show a progress indicator for fixed number of requests."""
        try:
            while True:
                completed = self.results["successful"] + self.results["failed"] + self.results["timeouts"]
                percent = (completed / total_requests) * 100
                elapsed = time.time() - self.results["start_time"]
                
                print(f"\rProgress: {completed}/{total_requests} ({percent:.1f}%) - "
                      f"Elapsed: {elapsed:.1f}s - "
                      f"RPS: {completed/elapsed:.1f}", end="")
                
                await asyncio.sleep(0.5)
        except asyncio.CancelledError:
            print("\rProgress tracking cancelled                                                ", end="\n")
            raise
    
    async def _show_duration_progress(self, total_duration):
        """Show a progress indicator for time-based test."""
        try:
            while True:
                completed = self.results["successful"] + self.results["failed"] + self.results["timeouts"]
                elapsed = time.time() - self.results["start_time"]
                percent = min(100, (elapsed / total_duration) * 100)
                remaining = max(0, total_duration - elapsed)
                
                print(f"\rElapsed: {elapsed:.1f}s/{total_duration}s ({percent:.1f}%) - "
                      f"Remaining: {remaining:.1f}s - "
                      f"Requests: {completed} - "
                      f"RPS: {completed/elapsed:.1f}", end="")
                
                await asyncio.sleep(0.5)
        except asyncio.CancelledError:
            print("\rProgress tracking cancelled                                                ", end="\n")
            raise
    
    def _print_summary(self):
        """Print a summary of the test results."""
        total_time = self.results["end_time"] - self.results["start_time"]
        completed = self.results["successful"] + self.results["failed"] + self.results["timeouts"]
        
        print("\n\n📊 API Stress Test Summary:")
        print(f"✅ Successful requests: {self.results['successful']} ({(self.results['successful']/completed)*100:.1f}%)")
        print(f"❌ Failed requests: {self.results['failed']} ({(self.results['failed']/completed)*100:.1f}%)")
        print(f"⏱️ Timeouts: {self.results['timeouts']} ({(self.results['timeouts']/completed)*100:.1f}%)")
        print(f"⏱️ Total time: {total_time:.2f} seconds")
        print(f"🔄 Requests per second (RPS): {completed/total_time:.2f}")
        print(f"📈 Concurrency level: {self.concurrency}")
        
        # Save results to file
        self._save_results()
    
    def _save_results(self):
        """Save test results to a file."""
        filename = f"api_stress_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(filename, "w") as f:
            f.write("API Stress Test Results\n")
            f.write("=====================\n\n")
            
            total_time = self.results["end_time"] - self.results["start_time"]
            completed = self.results["successful"] + self.results["failed"] + self.results["timeouts"]
            
            f.write(f"Test Date: {datetime.now().isoformat()}\n")
            f.write(f"Target API: {BASE_URL}\n\n")
            
            f.write(f"Total Requests: {completed}\n")
            f.write(f"Successful Requests: {self.results['successful']} ({(self.results['successful']/completed)*100:.1f}%)\n")
            f.write(f"Failed Requests: {self.results['failed']} ({(self.results['failed']/completed)*100:.1f}%)\n")
            f.write(f"Timeouts: {self.results['timeouts']} ({(self.results['timeouts']/completed)*100:.1f}%)\n")
            f.write(f"Total Test Duration: {total_time:.2f} seconds\n")
            f.write(f"Requests Per Second: {completed/total_time:.2f}\n")
            f.write(f"Concurrency Level: {self.concurrency}\n")
        
        print(f"✅ Results saved to {filename}")

async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="API Stress Testing Tool")
    parser.add_argument("--concurrency", type=int, default=DEFAULT_CONCURRENCY, 
                        help=f"Number of concurrent requests (default: {DEFAULT_CONCURRENCY})")
    
    # Group for mutually exclusive options
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument("--requests", type=int, help="Number of requests to make")
    group.add_argument("--duration", type=int, default=DEFAULT_DURATION,
                       help=f"Duration of the test in seconds (default: {DEFAULT_DURATION})")
    
    args = parser.parse_args()
    
    # Create the stress tester
    tester = APIStressTester(concurrency=args.concurrency)
    
    # Get entity IDs
    await tester.discover_ids()
    
    # Run the stress test (using duration by default)
    if args.requests:
        await tester.run_requests(args.requests)
    else:
        duration = args.duration if args.duration else DEFAULT_DURATION
        await tester.run_for_duration(duration)

if __name__ == "__main__":
    asyncio.run(main()) 