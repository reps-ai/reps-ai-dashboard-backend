#!/usr/bin/env python3
import asyncio
import argparse
import sys
import os
from sqlalchemy import text
from datetime import datetime, timedelta
import random
import uuid

# Add the parent directory to sys.path to allow importing from backend
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import our database connection
from backend.db.connections.database import get_db_session

async def execute_query(query, params=None):
    """Execute a SQL query against the Neon database."""
    session = await get_db_session()
    try:
        result = await session.execute(text(query), params)
        if query.strip().lower().startswith(("select", "show")):
            # For queries that return data
            columns = result.keys()
            rows = [dict(zip(columns, row)) for row in result.fetchall()]
            return rows
        else:
            # For queries that modify data (INSERT, UPDATE, DELETE)
            await session.commit()
            return {"message": "Query executed successfully"}
    except Exception as e:
        await session.rollback()
        raise e
    finally:
        await session.close()

async def check_connection():
    """Check if we can connect to the database."""
    session = await get_db_session()
    try:
        result = await session.execute(text("SELECT current_database(), current_user"))
        row = result.fetchone()
        return {
            "database": row[0],
            "user": row[1],
            "connection": "success"
        }
    finally:
        await session.close()

async def list_tables():
    """List all tables in the current schema."""
    return await execute_query("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name
    """)

async def describe_table(table_name):
    """Describe the structure of a table."""
    return await execute_query(f"""
        SELECT 
            column_name, 
            data_type, 
            is_nullable, 
            column_default
        FROM 
            information_schema.columns
        WHERE 
            table_schema = 'public' AND 
            table_name = '{table_name}'
        ORDER BY 
            ordinal_position
    """)

async def generate_mock_leads(count, branch_id, gym_id):
    """Generate realistic mock data for leads table."""
    # Common first and last names for realistic data
    first_names = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda", 
                  "William", "Elizabeth", "David", "Susan", "Richard", "Jessica", "Joseph", "Sarah",
                  "Thomas", "Karen", "Charles", "Lisa", "Christopher", "Nancy", "Daniel", "Betty",
                  "Matthew", "Sandra", "Anthony", "Margaret", "Mark", "Ashley", "Donald", "Kimberly",
                  "Steven", "Emily", "Andrew", "Donna", "Paul", "Michelle", "Joshua", "Carol"]
    
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
                 "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
                 "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
                 "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker",
                 "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Adams"]
    
    # Phone area codes for realistic numbers
    area_codes = ["201", "202", "203", "205", "206", "207", "208", "209", "210", "212", 
                 "213", "214", "215", "216", "217", "218", "219", "224", "225", "228",
                 "229", "231", "234", "239", "240", "248", "251", "252", "253", "254"]
    
    # Lead statuses (matching column name and realistic values)
    statuses = ["new", "contacted", "qualified", "appointment_scheduled", "converted", "lost"]
    
    # Lead sources
    sources = ["website", "referral", "social_media", "walk_in", "promotion", "google", "facebook", "instagram"]
    
    # Fitness goals
    fitness_goals = [
        "Weight loss",
        "Muscle gain",
        "Improve overall fitness",
        "Training for specific event",
        "Rehabilitation from injury",
        "Sports performance",
        "General health improvement",
        "Stress reduction"
    ]
    
    # Budget ranges
    budget_ranges = ["$50-100/month", "$100-150/month", "$150-200/month", "$200+/month"]
    
    # Timeframes
    timeframes = ["Immediately", "Within 1 week", "Within 1 month", "Next 3 months", "Just exploring"]
    
    # Contact methods
    contact_methods = ["phone", "email", "text", "any"]
    
    # Contact times
    contact_times = ["Morning", "Afternoon", "Evening", "Weekends only", "Weekdays only", "Anytime"]
    
    # Urgency levels
    urgency_levels = ["high", "medium", "low"]
    
    # Fitness levels
    fitness_levels = ["beginner", "intermediate", "advanced", "professional"]
    
    # Training types
    training_types = [
        "Personal training",
        "Group fitness classes",
        "Strength training",
        "Cardio",
        "Yoga/Pilates",
        "CrossFit style",
        "Functional training",
        "Sports-specific"
    ]
    
    # Create lead records
    leads = []
    now = datetime.now()
    
    for i in range(count):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        email = f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 999)}@example.com"
        phone = f"{random.choice(area_codes)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
        
        # Random date in the past 90 days
        created_at = now - timedelta(days=random.randint(0, 90))
        
        # Build the lead record with all possible fields from schema
        lead = {
            "id": str(uuid.uuid4()),
            "branch_id": branch_id,
            "gym_id": gym_id,
            "first_name": first_name,
            "last_name": last_name,
            "phone": phone,
            "email": email if random.random() > 0.1 else None,  # some might not have email
            "lead_status": random.choice(statuses),
            "source": random.choice(sources) if random.random() > 0.2 else None,
            "created_at": created_at,
            "updated_at": created_at,  # Start with same as created
        }
        
        # Randomly add optional fields with varying probabilities
        
        # 70% chance to have notes
        if random.random() > 0.3:
            lead["notes"] = random.choice([
                "Interested in membership options",
                "Looking for personal training",
                "Wants to try a class first",
                "Former member considering rejoining",
                "Wants family membership info",
                "Referred by current member",
                "Price sensitive, looking for deals",
                "Interested in nutrition coaching"
            ])
        
        # 50% chance to have score
        if random.random() > 0.5:
            lead["score"] = random.randint(1, 100)
        
        # 40% chance to have a qualification score
        if random.random() > 0.6:
            lead["qualification_score"] = random.randint(1, 10)
            
        # 30% chance to have qualification notes
        if random.random() > 0.7:
            lead["qualification_notes"] = random.choice([
                "Good potential",
                "Needs follow-up",
                "Price sensitive",
                "Ready to commit",
                "Unsure about commitment"
            ])
        
        # 60% chance to have specific interest
        if random.random() > 0.4:
            lead["interest"] = random.choice([
                "Personal Training",
                "Group Classes",
                "Membership",
                "Nutrition Coaching",
                "Weight Loss Program"
            ])
        
        # 40% chance to have interest location
        if random.random() > 0.6:
            lead["interest_location"] = random.choice([
                "Main Location",
                "Downtown Branch",
                "North Side",
                "Virtual/Online"
            ])
        
        # 30% chance to have last conversation summary
        if random.random() > 0.7:
            lead["last_conversation_summary"] = random.choice([
                "Discussed membership options and pricing",
                "Scheduled a facility tour",
                "Inquired about class schedule",
                "Asked about personal training rates",
                "Wanted information about childcare services",
                "Interested in nutrition programs"
            ])
        
        # 25% chance to have been called recently
        if random.random() > 0.75:
            last_called_days = random.randint(0, 30)
            lead["last_called"] = created_at + timedelta(days=last_called_days)
        
        # 20% chance to have an upcoming appointment
        if random.random() > 0.8:
            appointment_days = random.randint(1, 14)
            lead["next_appointment_date"] = now + timedelta(days=appointment_days)
        
        # Add specific fitness-related fields
        
        # 50% chance to have fitness goals
        if random.random() > 0.5:
            num_goals = random.randint(1, 3)
            selected_goals = random.sample(fitness_goals, num_goals)
            lead["fitness_goals"] = ", ".join(selected_goals)
        
        # 40% chance to have budget range
        if random.random() > 0.6:
            lead["budget_range"] = random.choice(budget_ranges)
        
        # 60% chance to have timeframe
        if random.random() > 0.4:
            lead["timeframe"] = random.choice(timeframes)
        
        # 50% chance to have preferred contact method
        if random.random() > 0.5:
            lead["preferred_contact_method"] = random.choice(contact_methods)
        
        # 40% chance to have preferred contact time
        if random.random() > 0.6:
            lead["preferred_contact_time"] = random.choice(contact_times)
        
        # 30% chance to have urgency
        if random.random() > 0.7:
            lead["urgency"] = random.choice(urgency_levels)
        
        # 45% chance to have fitness level
        if random.random() > 0.55:
            lead["fitness_level"] = random.choice(fitness_levels)
        
        # 70% chance to have previous gym experience
        if random.random() > 0.3:
            lead["previous_gym_experience"] = random.choice([True, False])
        
        # 35% chance to have specific health goals
        if random.random() > 0.65:
            lead["specific_health_goals"] = random.choice([
                "Lower blood pressure",
                "Manage diabetes",
                "Improve cardiovascular health",
                "Reduce back pain",
                "Improve mobility",
                "Increase energy levels",
                "Better sleep"
            ])
        
        # 40% chance to have preferred training type
        if random.random() > 0.6:
            num_types = random.randint(1, 2)
            selected_types = random.sample(training_types, num_types)
            lead["preferred_training_type"] = ", ".join(selected_types)
        
        # 25% chance to have availability
        if random.random() > 0.75:
            lead["availability"] = random.choice([
                "Weekday mornings",
                "Weekday evenings",
                "Weekends only",
                "Flexible schedule",
                "Monday/Wednesday/Friday",
                "Tuesday/Thursday"
            ])
        
        # 15% chance to have medical conditions
        if random.random() > 0.85:
            lead["medical_conditions"] = random.choice([
                "None",
                "Back issues",
                "Knee problems",
                "High blood pressure",
                "Diabetes",
                "Asthma",
                "Pregnancy",
                "Recent surgery"
            ])
            
        # Assign a user if needed (randomly do this 40% of the time)
        if random.random() > 0.6:
            # First get a valid user ID from users table
            users = await execute_query("SELECT id FROM users LIMIT 10")
            if users and len(users) > 0:
                user_id = random.choice(users)["id"]
                lead["assigned_to_user_id"] = user_id
        
        leads.append(lead)
    
    # Insert the leads into the database
    inserted_count = 0
    for lead in leads:
        # Build the insert statement dynamically based on the lead fields
        columns = ", ".join(lead.keys())
        placeholders = ", ".join([f":{k}" for k in lead.keys()])
        
        query = f"""
        INSERT INTO leads ({columns})
        VALUES ({placeholders})
        """
        
        try:
            await execute_query(query, lead)
            inserted_count += 1
        except Exception as e:
            print(f"Error inserting lead: {e}")
    
    return {"message": f"Successfully inserted {inserted_count} mock leads"}

def parse_args():
    parser = argparse.ArgumentParser(description='Neon Database Helper Script')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Check connection command
    subparsers.add_parser('check', help='Check database connection')
    
    # List tables command
    subparsers.add_parser('tables', help='List all tables in the database')
    
    # Describe table command
    describe_parser = subparsers.add_parser('describe', help='Describe table structure')
    describe_parser.add_argument('table', help='Table name to describe')
    
    # Generate mock leads command
    mock_parser = subparsers.add_parser('genleads', help='Generate mock leads data')
    mock_parser.add_argument('count', type=int, help='Number of mock leads to generate')
    mock_parser.add_argument('--branch', required=True, help='Branch ID to assign to leads')
    mock_parser.add_argument('--gym', required=True, help='Gym ID to assign to leads')
    
    # Query command
    query_parser = subparsers.add_parser('query', help='Execute a SQL query')
    query_parser.add_argument('sql', help='SQL query to execute')
    
    return parser.parse_args()

async def main():
    args = parse_args()
    
    if args.command == 'check':
        result = await check_connection()
        print(f"Connection successful to database '{result['database']}' as user '{result['user']}'")
        
    elif args.command == 'tables':
        tables = await list_tables()
        if tables:
            print("Tables in database:")
            for table in tables:
                print(f"- {table['table_name']}")
        else:
            print("No tables found in database")
    
    elif args.command == 'describe':
        columns = await describe_table(args.table)
        if columns:
            print(f"Structure of table '{args.table}':")
            for col in columns:
                nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
                default = f"DEFAULT {col['column_default']}" if col['column_default'] else ""
                print(f"- {col['column_name']} ({col['data_type']}) {nullable} {default}")
        else:
            print(f"Table '{args.table}' not found or has no columns")
            
    elif args.command == 'genleads':
        result = await generate_mock_leads(args.count, args.branch, args.gym)
        print(result["message"])
            
    elif args.command == 'query':
        result = await execute_query(args.sql)
        if isinstance(result, list):
            if result:
                # Pretty print the results
                for row in result:
                    print(row)
            else:
                print("Query returned no results")
        else:
            print(result["message"])
    
    else:
        print("Please specify a command: check, tables, describe, genleads, or query")

if __name__ == "__main__":
    asyncio.run(main()) 