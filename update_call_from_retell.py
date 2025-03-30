"""
Script to fetch and update call data from Retell.

This script can be used to manually update a call record with the latest data from Retell.
Useful for cases where a webhook might have been missed or for testing.
"""
import asyncio
import sys
from datetime import datetime
from typing import Dict, Any

from retell import Retell
from backend.db.connections.database import SessionLocal
from backend.db.repositories.call.implementations import PostgresCallRepository
from backend.utils.logging.logger import get_logger

logger = get_logger(__name__)

# Load environment variables
import os
from dotenv import load_dotenv
load_dotenv()

async def update_call_from_retell(internal_call_id: str, retell_call_id: str):
    """
    Fetch call data from Retell and update our database record.
    
    Args:
        internal_call_id: Our internal call ID (database primary key)
        retell_call_id: Retell's call ID
    """
    logger.info(f"Updating call {internal_call_id} with data from Retell call {retell_call_id}")
    
    # Initialize Retell client
    retell_api_key = os.getenv("RETELL_API_KEY")
    if not retell_api_key:
        logger.error("RETELL_API_KEY not found in environment variables")
        return False
        
    try:
        retell_client = Retell(api_key=retell_api_key)
        
        # Fetch call data from Retell
        logger.info(f"Fetching call data from Retell for call ID: {retell_call_id}")
        retell_call = retell_client.call.retrieve(retell_call_id)
        
        if not retell_call:
            logger.error(f"Call {retell_call_id} not found in Retell")
            return False
            
        logger.info(f"Retrieved call data from Retell: {retell_call}")
        
        # Convert to dictionary
        if hasattr(retell_call, 'to_dict'):
            retell_data = retell_call.to_dict()
        else:
            retell_data = dict(retell_call)
        
        # Get database session
        db = SessionLocal()
        try:
            # Create call repository
            call_repository = PostgresCallRepository(db)
            
            # Get current call data
            current_call = await call_repository.get_call_by_id(internal_call_id)
            if not current_call:
                logger.error(f"Call {internal_call_id} not found in database")
                return False
                
            # Prepare update data
            update_data = {}
            
            # Update status if provided
            if retell_data.get("call_status"):
                if retell_data["call_status"] == "ended":
                    update_data["call_status"] = "completed"
                elif retell_data["call_status"] == "ongoing":
                    update_data["call_status"] = "in_progress"
                else:
                    update_data["call_status"] = retell_data["call_status"]
            
            # Update timestamps if provided
            if retell_data.get("start_timestamp"):
                update_data["start_time"] = datetime.fromtimestamp(retell_data["start_timestamp"] / 1000)
                
            if retell_data.get("end_timestamp"):
                update_data["end_time"] = datetime.fromtimestamp(retell_data["end_timestamp"] / 1000)
                
                # Calculate duration if both timestamps are available
                if retell_data.get("start_timestamp"):
                    duration_ms = retell_data["end_timestamp"] - retell_data["start_timestamp"]
                    update_data["duration"] = int(duration_ms / 1000)
            
            # Update media and analysis if available
            if retell_data.get("recording_url"):
                update_data["recording_url"] = retell_data["recording_url"]
                
            if retell_data.get("transcript"):
                update_data["transcript"] = retell_data["transcript"]
                
            # Call analysis data
            if retell_data.get("call_analysis"):
                analysis = retell_data["call_analysis"]
                
                if analysis.get("call_summary"):
                    update_data["summary"] = analysis["call_summary"]
                    
                if analysis.get("user_sentiment"):
                    update_data["sentiment"] = analysis["user_sentiment"].lower()
            
            # Update the call record
            if update_data:
                logger.info(f"Updating call {internal_call_id} with data: {update_data}")
                updated_call = await call_repository.update_call(internal_call_id, update_data)
                
                if updated_call:
                    logger.info(f"Successfully updated call {internal_call_id}")
                    return True
                else:
                    logger.error(f"Failed to update call {internal_call_id}")
                    return False
            else:
                logger.info(f"No update data found for call {internal_call_id}")
                return False
                
        finally:
            await db.close()
            
    except Exception as e:
        logger.error(f"Error updating call from Retell: {str(e)}")
        return False

# Main function to run from command line
async def main():
    """Run the script from command line."""
    if len(sys.argv) < 3:
        print("Usage: python update_call_from_retell.py <internal_call_id> <retell_call_id>")
        return
        
    internal_call_id = sys.argv[1]
    retell_call_id = sys.argv[2]
    
    result = await update_call_from_retell(internal_call_id, retell_call_id)
    if result:
        print(f"Successfully updated call {internal_call_id} with Retell data")
    else:
        print(f"Failed to update call {internal_call_id}")

if __name__ == "__main__":
    asyncio.run(main()) 