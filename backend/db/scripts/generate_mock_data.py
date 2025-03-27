"""
Script to generate mock data for the Reps AI Dashboard database.
This will populate essential tables with realistic mock data.
"""
import os
import random
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import uuid
import json
from faker import Faker

# Configuration
from dotenv import load_dotenv
load_dotenv()

# Get the database URL from .env
DATABASE_URL = os.getenv("DATABASE_URL", "").replace('+asyncpg', '')

# Initialize faker
fake = Faker()

# Constants for mock data generation
LEAD_STATUS_OPTIONS = ["new", "contacted", "qualified", "converted", "closed"]
LEAD_SOURCES = ["website", "referral", "walk-in", "social media", "online ad", "event"]
USER_ROLES = ["admin", "manager", "agent"]
APPOINTMENT_TYPES = ["tour", "consultation", "training", "follow-up"]
APPOINTMENT_STATUSES = ["scheduled", "completed", "cancelled", "no_show"]
CALL_TYPES = ["outbound", "inbound"]
CALL_OUTCOMES = ["scheduled", "not_interested", "callback", "left_message", "no_answer"]
INTEREST_OPTIONS = ["weight loss", "muscle gain", "general fitness", "specialized training", "group classes"]
FITNESS_LEVELS = ["beginner", "intermediate", "advanced"]
BUDGET_RANGES = ["$20-50/month", "$50-100/month", "$100-200/month", "$200+/month"]

# Helper function to generate short phone numbers
def generate_phone():
    return f"555-{random.randint(1000, 9999)}"

def create_mock_data():
    """Generate and insert mock data using SQL."""
    # Create database connection
    engine = create_engine(DATABASE_URL)
    conn = engine.connect()
    
    try:
        # Start a transaction
        trans = conn.begin()
        
        # Create mock gyms
        print("Creating mock gyms...")
        gym_ids = create_gyms(conn)
        
        # Create mock branches
        print("Creating mock branches...")
        branch_ids = create_branches(conn, gym_ids)
        
        # Create mock users
        print("Creating mock users...")
        user_ids = create_users(conn, gym_ids, branch_ids)
        
        # Create mock tags
        print("Creating mock tags...")
        tag_ids = create_tags(conn)
        
        # Create mock leads
        print("Creating mock leads...")
        lead_ids = create_leads(conn, gym_ids, branch_ids, user_ids)
        
        # Create mock lead_tag associations
        print("Creating lead-tag associations...")
        create_lead_tags(conn, lead_ids, tag_ids)
        
        # Create mock members (converted leads)
        print("Creating mock members...")
        create_members(conn, lead_ids, gym_ids, branch_ids)
        
        # Create mock appointments
        print("Creating mock appointments...")
        create_appointments(conn, lead_ids, gym_ids, branch_ids, user_ids)
        
        # Create mock AI settings
        print("Creating mock AI settings...")
        create_ai_settings(conn, gym_ids, branch_ids)
        
        # Create mock Voice settings
        print("Creating mock Voice settings...")
        create_voice_settings(conn, gym_ids, branch_ids)
        
        # Create mock call settings
        print("Creating mock call settings...")
        create_call_settings(conn, gym_ids, branch_ids)
        
        # Create mock call logs
        print("Creating mock call logs...")
        create_call_logs(conn, gym_ids, branch_ids, lead_ids)
        
        # Create mock follow-up calls
        print("Creating mock follow-up calls...")
        create_follow_up_calls(conn, gym_ids, branch_ids, lead_ids)
        
        # Create mock follow-up campaigns
        print("Creating mock follow-up campaigns...")
        create_follow_up_campaigns(conn, gym_ids, branch_ids, lead_ids)
        
        # Create mock knowledge base records
        print("Creating mock knowledge base records...")
        create_knowledge_base(conn, gym_ids, branch_ids)
        
        # Create mock gym settings
        print("Creating mock gym settings...")
        create_gym_settings(conn, gym_ids, branch_ids)
        
        # Commit the transaction
        trans.commit()
        print("Mock data created successfully!")
        
    except Exception as e:
        if 'trans' in locals() and trans:
            trans.rollback()
        print(f"Error creating mock data: {str(e)}")
        raise
    finally:
        conn.close()
        engine.dispose()

def create_gyms(conn):
    """Create mock gym records."""
    gym_ids = []
    
    for i in range(3):
        gym_id = str(uuid.uuid4())
        gym_ids.append(gym_id)
        
        conn.execute(text(f"""
        INSERT INTO gyms (id, name, address, phone, is_active)
        VALUES 
        ('{gym_id}', '{fake.company()} Fitness', '{fake.street_address()}', '{generate_phone()}', true)
        """))
    
    return gym_ids

def create_branches(conn, gym_ids):
    """Create mock branch records."""
    branch_ids = []
    
    for gym_id in gym_ids:
        # Create 2 branches per gym
        for i in range(2):
            branch_id = str(uuid.uuid4())
            branch_ids.append(branch_id)
            
            conn.execute(text(f"""
            INSERT INTO branches (id, gym_id, name, address, phone, email, is_active)
            VALUES 
            ('{branch_id}', '{gym_id}', '{fake.company()} - {fake.city()}', '{fake.street_address()}', 
            '{generate_phone()}', '{fake.email()}', true)
            """))
    
    return branch_ids

def create_users(conn, gym_ids, branch_ids):
    """Create mock user records."""
    user_ids = []
    
    # Create admin users for each gym
    for gym_id in gym_ids:
        user_id = str(uuid.uuid4())
        user_ids.append(user_id)
        first_name = fake.first_name()
        last_name = fake.last_name()
        
        conn.execute(text(f"""
        INSERT INTO users (id, gym_id, username, password_hash, email, first_name, last_name, role, is_active)
        VALUES 
        ('{user_id}', '{gym_id}', '{first_name.lower()}.{last_name.lower()}', 
        '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', '{fake.email()}',
        '{first_name}', '{last_name}', 'admin', true)
        """))
    
    # Create branch-specific users
    for branch_id in branch_ids:
        # Get the gym_id for this branch
        gym_id = None
        for g_id in gym_ids:
            result = conn.execute(text(f"SELECT gym_id FROM branches WHERE id = '{branch_id}'")).fetchone()
            if result:
                gym_id = result[0]
                break
        
        if gym_id:
            # Create 3-5 users per branch with different roles
            for i in range(random.randint(3, 5)):
                user_id = str(uuid.uuid4())
                user_ids.append(user_id)
                first_name = fake.first_name()
                last_name = fake.last_name()
                role = random.choice(USER_ROLES)
                
                conn.execute(text(f"""
                INSERT INTO users (id, gym_id, branch_id, username, password_hash, email, first_name, last_name, 
                role, phone, profile_picture, is_active)
                VALUES 
                ('{user_id}', '{gym_id}', '{branch_id}', '{first_name.lower()}.{last_name.lower()}_{i}', 
                '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', '{fake.email()}',
                '{first_name}', '{last_name}', '{role}', '{generate_phone()}', 
                'https://randomuser.me/api/portraits/{'men' if random.random() > 0.5 else 'women'}/{random.randint(1, 99)}.jpg', true)
                """))
    
    return user_ids

def create_tags(conn):
    """Create mock tag records."""
    tag_names = ["Interested", "Hot Lead", "Cold Lead", "Needs Follow-up", "VIP", 
                "High Budget", "Low Budget", "Personal Training", "Group Classes", 
                "Weight Loss", "Muscle Gain", "Senior", "Student"]
    
    tag_ids = []
    for name in tag_names:
        tag_id = str(uuid.uuid4())
        tag_ids.append(tag_id)
        color = f"#{random.randint(0, 0xFFFFFF):06x}"
        
        conn.execute(text(f"""
        INSERT INTO tags (id, name, color)
        VALUES ('{tag_id}', '{name}', '{color}')
        """))
    
    return tag_ids

def create_leads(conn, gym_ids, branch_ids, user_ids):
    """Create mock lead records."""
    lead_ids = []
    
    # Create 10-20 leads per branch
    for branch_id in branch_ids:
        # Get the gym_id for this branch
        result = conn.execute(text(f"SELECT gym_id FROM branches WHERE id = '{branch_id}'")).fetchone()
        if not result:
            continue
            
        gym_id = result[0]
        
        # Find users for this branch
        branch_users = conn.execute(text(f"SELECT id FROM users WHERE branch_id = '{branch_id}'")).fetchall()
        branch_user_ids = [u[0] for u in branch_users]
        
        # Create leads
        num_leads = random.randint(10, 20)
        for i in range(num_leads):
            lead_id = str(uuid.uuid4())
            lead_ids.append(lead_id)
            
            assigned_user_id = random.choice(branch_user_ids) if branch_user_ids else None
            lead_status = random.choice(LEAD_STATUS_OPTIONS)
            source = random.choice(LEAD_SOURCES)
            interest = random.choice(INTEREST_OPTIONS) if random.random() > 0.2 else None
            score = random.randint(1, 100) if random.random() > 0.3 else None
            
            # Format timestamps as strings
            created_at = datetime.now() - timedelta(days=random.randint(1, 90))
            created_at_str = created_at.strftime("%Y-%m-%d %H:%M:%S")
            
            last_called = created_at + timedelta(days=random.randint(1, 30)) if random.random() > 0.4 else None
            last_called_str = last_called.strftime("%Y-%m-%d %H:%M:%S") if last_called else None
            
            next_appointment_date = datetime.now() + timedelta(days=random.randint(1, 30)) if random.random() > 0.5 else None
            next_appointment_date_str = next_appointment_date.strftime("%Y-%m-%d %H:%M:%S") if next_appointment_date else None
            
            # Handle nullable fields
            interest_sql = f"'{interest}'" if interest else "NULL"
            score_sql = str(score) if score else "NULL"
            last_called_sql = f"'{last_called_str}'" if last_called else "NULL"
            next_appointment_sql = f"'{next_appointment_date_str}'" if next_appointment_date else "NULL"
            assigned_user_sql = f"'{assigned_user_id}'" if assigned_user_id else "NULL"
            
            # Shorten notes to avoid issues
            notes = fake.sentence()
            
            conn.execute(text(f"""
            INSERT INTO leads (
                id, branch_id, gym_id, assigned_to_user_id, first_name, last_name, phone, email, 
                lead_status, notes, interest, score, source, last_called, next_appointment_date, created_at
            )
            VALUES (
                '{lead_id}', '{branch_id}', '{gym_id}', {assigned_user_sql}, '{fake.first_name()}', 
                '{fake.last_name()}', '{generate_phone()}', '{fake.email()}', '{lead_status}', 
                '{notes}', {interest_sql}, {score_sql}, '{source}', {last_called_sql}, 
                {next_appointment_sql}, '{created_at_str}'
            )
            """))
    
    return lead_ids

def create_lead_tags(conn, lead_ids, tag_ids):
    """Create lead-tag associations."""
    for lead_id in lead_ids:
        # Add 0-3 random tags to each lead
        num_tags = random.randint(0, 3)
        if num_tags > 0:
            selected_tag_ids = random.sample(tag_ids, min(num_tags, len(tag_ids)))
            
            for tag_id in selected_tag_ids:
                # Add current timestamp for created_at
                created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                conn.execute(text(f"""
                INSERT INTO lead_tag (lead_id, tag_id, created_at)
                VALUES ('{lead_id}', '{tag_id}', '{created_at}')
                """))

def create_members(conn, lead_ids, gym_ids, branch_ids):
    """Create mock member records from converted leads."""
    # Convert about 30% of leads to members
    for lead_id in lead_ids:
        if random.random() < 0.3:
            # Get the lead information
            lead_info = conn.execute(text(f"SELECT gym_id, branch_id FROM leads WHERE id = '{lead_id}'")).fetchone()
            if not lead_info:
                continue
                
            gym_id, branch_id = lead_info
            
            # Update lead status to converted
            conn.execute(text(f"UPDATE leads SET lead_status = 'converted' WHERE id = '{lead_id}'"))
            
            # Create a member
            member_id = str(uuid.uuid4())
            
            membership_start = datetime.now() - timedelta(days=random.randint(1, 60))
            membership_start_str = membership_start.strftime("%Y-%m-%d %H:%M:%S")
            
            membership_type = random.choice(["Basic", "Premium", "Gold", "VIP", "Monthly", "Annual"])
            membership_status = random.choice(["active", "inactive", "cancelled", "suspended"])
            payment_method = random.choice(["credit_card", "debit_card", "bank_transfer", "cash"])
            
            conn.execute(text(f"""
            INSERT INTO members (
                id, gym_id, lead_id, branch_id, membership_start_date, membership_type, 
                membership_status, payment_method
            )
            VALUES (
                '{member_id}', '{gym_id}', '{lead_id}', '{branch_id}', '{membership_start_str}',
                '{membership_type}', '{membership_status}', '{payment_method}'
            )
            """))

def create_appointments(conn, lead_ids, gym_ids, branch_ids, user_ids):
    """Create mock appointment records."""
    # Create 1-3 appointments for about 60% of leads
    for lead_id in lead_ids:
        if random.random() < 0.6:
            # Get the lead information
            lead_info = conn.execute(text(f"SELECT gym_id, branch_id FROM leads WHERE id = '{lead_id}'")).fetchone()
            if not lead_info:
                continue
                
            gym_id, branch_id = lead_info
            
            # Find users for this branch
            branch_users = conn.execute(text(f"SELECT id, first_name, last_name FROM users WHERE branch_id = '{branch_id}'")).fetchall()
            
            # Create 1-3 appointments
            num_appointments = random.randint(1, 3)
            for i in range(num_appointments):
                appointment_id = str(uuid.uuid4())
                
                # Choose random users for employee and creator
                employee = random.choice(branch_users) if branch_users else None
                creator = random.choice(branch_users) if branch_users else None
                
                # Determine if appointment is past or future
                if i == 0 and random.random() < 0.7:
                    # First appointment more likely to be in the past
                    appointment_date = datetime.now() - timedelta(days=random.randint(1, 30))
                    status = random.choice(["completed", "cancelled", "no_show"])
                else:
                    # Subsequent appointments more likely to be in the future
                    appointment_date = datetime.now() + timedelta(days=random.randint(1, 30))
                    status = "scheduled"
                
                appointment_date_str = appointment_date.strftime("%Y-%m-%d %H:%M:%S")
                
                # Handle nullable fields
                employee_id_sql = f"'{employee[0]}'" if employee else "NULL"
                created_by_id_sql = f"'{creator[0]}'" if creator else "NULL"
                employee_name_sql = f"'{employee[1]} {employee[2]}'" if employee else f"'{fake.first_name()} {fake.last_name()}'"
                
                # Short notes to avoid issues
                notes = fake.sentence()
                
                conn.execute(text(f"""
                INSERT INTO appointments (
                    id, gym_id, lead_id, branch_id, employee_user_id, appointment_type, appointment_date,
                    duration, appointment_status, notes, created_by_user_id, reminder_sent, employee_name
                )
                VALUES (
                    '{appointment_id}', '{gym_id}', '{lead_id}', '{branch_id}', {employee_id_sql},
                    '{random.choice(APPOINTMENT_TYPES)}', '{appointment_date_str}', {random.choice([30, 45, 60, 90])},
                    '{status}', '{notes}', {created_by_id_sql},
                    {str(random.choice([True, False])).lower()}, {employee_name_sql}
                )
                """))

def create_ai_settings(conn, gym_ids, branch_ids, n=3):
    """Create mock AI settings records."""
    ai_ids = []
    for _ in range(n):
        ai_id = str(uuid.uuid4())
        ai_ids.append(ai_id)
        gym_id = random.choice(gym_ids)
        branch_id = random.choice(branch_ids)
        personality = random.choice(["friendly", "formal", "casual"])
        agent_name = fake.first_name()
        greeting = "Hello, how can I help you?"
        allow_interruptions = random.choice([True, False])
        offer_human_transfer = random.choice([True, False])
        escalation_threshold = random.randint(1, 10)
        conn.execute(text(f"""
        INSERT INTO ai_settings (id, gym_id, branch_id, personality, agent_name, greeting, allow_interruptions, offer_human_transfer, escalation_threshold, created_at)
        VALUES ('{ai_id}', '{gym_id}', '{branch_id}', '{personality}', '{agent_name}', '{greeting}', {str(allow_interruptions).lower()}, {str(offer_human_transfer).lower()}, {escalation_threshold}, '{datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
        """))
    return ai_ids

def create_voice_settings(conn, gym_ids, branch_ids, n=3):
    """Create mock Voice settings records."""
    vs_ids = []
    for _ in range(n):
        vs_id = str(uuid.uuid4())
        vs_ids.append(vs_id)
        gym_id = random.choice(gym_ids)
        branch_id = random.choice(branch_ids)
        voice_type = random.choice(["male", "female"])
        speaking_speed = random.choice(["slow", "normal", "fast"])
        volume = random.choice(["low", "medium", "high"])
        voice_sample_url = fake.url()
        conn.execute(text(f"""
        INSERT INTO voice_settings (id, gym_id, branch_id, voice_type, speaking_speed, volume, voice_sample_url, created_at)
        VALUES ('{vs_id}', '{gym_id}', '{branch_id}', '{voice_type}', '{speaking_speed}', '{volume}', '{voice_sample_url}', '{datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
        """))
    return vs_ids

def create_call_logs(conn, gym_ids, branch_ids, lead_ids, n=10):
    """Create mock call log records."""
    log_ids = []
    for _ in range(n):
        log_id = str(uuid.uuid4())
        log_ids.append(log_id)
        gym_id = random.choice(gym_ids)
        branch_id = random.choice(branch_ids)
        lead_id = random.choice(lead_ids)
        duration = random.randint(30, 300)
        call_type = random.choice(CALL_TYPES)
        human_notes = fake.text(max_nb_chars=100)
        outcome = random.choice(CALL_OUTCOMES)
        call_status = random.choice(["completed", "failed"])
        start_time = datetime.now() - timedelta(minutes=random.randint(10,60))
        end_time = datetime.now()
        recording_url = fake.url()
        transcript = fake.text(max_nb_chars=200)
        summary = fake.text(max_nb_chars=100)
        sentiment = random.choice(["positive", "negative", "neutral"])
        # campaign_id left NULL for now
        conn.execute(text(f"""
        INSERT INTO call_logs (id, branch_id, gym_id, lead_id, duration, call_type, human_notes, outcome, call_status, start_time, end_time, recording_url, transcript, summary, sentiment)
        VALUES ('{log_id}', '{branch_id}', '{gym_id}', '{lead_id}', {duration}, '{call_type}', '{human_notes}', '{outcome}', '{call_status}', '{start_time.strftime("%Y-%m-%d %H:%M:%S")}', '{end_time.strftime("%Y-%m-%d %H:%M:%S")}', '{recording_url}', '{transcript}', '{summary}', '{sentiment}')
        """))
    return log_ids

def create_call_settings(conn, gym_ids, branch_ids, n=3):
    """Create mock call settings records."""
    cs_ids = []
    for _ in range(n):
        cs_id = str(uuid.uuid4())
        cs_ids.append(cs_id)
        gym_id = random.choice(gym_ids)
        branch_id = random.choice(branch_ids)
        max_duration = random.randint(30, 300)
        call_hours_start = "09:00"
        call_hours_end = "17:00"
        active_call_days = json.dumps(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
        retry_attempts = random.randint(1, 3)
        retry_interval = random.randint(1, 4)
        do_not_disturb = random.choice([True, False])
        conn.execute(text(f"""
        INSERT INTO call_settings (id, branch_id, gym_id, max_duration, call_hours_start, call_hours_end, active_call_days, retry_attempts, retry_interval, do_not_disturb, created_at)
        VALUES ('{cs_id}', '{branch_id}', '{gym_id}', {max_duration}, '{call_hours_start}', '{call_hours_end}', '{active_call_days}', {retry_attempts}, {retry_interval}, {str(do_not_disturb).lower()}, '{datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
        """))
    return cs_ids

def create_follow_up_calls(conn, gym_ids, branch_ids, lead_ids, n=5):
    """Create mock follow-up call records."""
    fuc_ids = []
    for _ in range(n):
        fuc_id = str(uuid.uuid4())
        fuc_ids.append(fuc_id)
        gym_id = random.choice(gym_ids)
        branch_id = random.choice(branch_ids)
        lead_id = random.choice(lead_ids)
        # campaign_id left NULL; could be updated later
        number_of_calls = random.randint(1, 5)
        call_date_time = datetime.now() - timedelta(days=random.randint(1,10))
        duration = random.randint(30, 300)
        call_type = random.choice(["outbound", "inbound", "ai"])
        human_notes = fake.text(max_nb_chars=100)
        outcome = random.choice(["scheduled", "not_interested", "callback"])
        call_status = random.choice(["scheduled", "in_progress", "completed", "failed"])
        recording_url = fake.url()
        transcript = fake.text(max_nb_chars=200)
        summary = fake.text(max_nb_chars=100)
        sentiment = random.choice(["positive", "negative", "neutral"])
        conn.execute(text(f"""
        INSERT INTO follow_up_calls (id, lead_id, branch_id, gym_id, number_of_calls, call_date_time, duration, call_type, human_notes, outcome, call_status, recording_url, transcript, summary, sentiment, created_at)
        VALUES ('{fuc_id}', '{lead_id}', '{branch_id}', '{gym_id}', {number_of_calls}, '{call_date_time.strftime("%Y-%m-%d %H:%M:%S")}', {duration}, '{call_type}', '{human_notes}', '{outcome}', '{call_status}', '{recording_url}', '{transcript}', '{summary}', '{sentiment}', '{datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
        """))
    return fuc_ids

def create_follow_up_campaigns(conn, gym_ids, branch_ids, lead_ids, n=3):
    """Create mock follow-up campaign records."""
    campaign_ids = []
    for _ in range(n):
        campaign_id = str(uuid.uuid4())
        campaign_ids.append(campaign_id)
        gym_id = random.choice(gym_ids)
        branch_id = random.choice(branch_ids)
        lead_id = random.choice(lead_ids)
        name = f"{fake.word()} Campaign"
        description = fake.text(max_nb_chars=150)
        start_date = datetime.now() - timedelta(days=random.randint(1,10))
        end_date = datetime.now() + timedelta(days=random.randint(10,30))
        frequency = random.randint(1,7)
        gap = random.randint(1,3)
        campaign_status = random.choice(["active", "completed", "paused", "cancelled"])
        conn.execute(text(f"""
        INSERT INTO follow_up_campaigns (id, lead_id, gym_id, branch_id, name, description, start_date, end_date, frequency, gap, campaign_status, created_at)
        VALUES ('{campaign_id}', '{lead_id}', '{gym_id}', '{branch_id}', '{name}', '{description}', '{start_date.strftime("%Y-%m-%d %H:%M:%S")}', '{end_date.strftime("%Y-%m-%d %H:%M:%S")}', {frequency}, {gap}, '{campaign_status}', '{datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
        """))
    return campaign_ids

def create_knowledge_base(conn, gym_ids, branch_ids, n=3):
    """Create mock knowledge base records."""
    kb_ids = []
    for _ in range(n):
        kb_id = str(uuid.uuid4())
        kb_ids.append(kb_id)
        gym_id = random.choice(gym_ids)
        branch_id = random.choice(branch_ids)
        pdf_url = fake.url()
        question = fake.sentence()
        answer = fake.paragraph()
        tags = json.dumps(["faq", "general"])
        conn.execute(text(f"""
        INSERT INTO knowledge_base (id, branch_id, gym_id, pdf_url, question, answer, tags, created_at)
        VALUES ('{kb_id}', '{branch_id}', '{gym_id}', '{pdf_url}', '{question}', '{answer}', '{tags}', '{datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
        """))
    return kb_ids

def create_gym_settings(conn, gym_ids, branch_ids, n=3):
    """Create mock gym settings records."""
    gs_ids = []
    for _ in range(n):
        gs_id = str(uuid.uuid4())
        gs_ids.append(gs_id)
        gym_id = random.choice(gym_ids)
        branch_id = random.choice(branch_ids)
        name = f"{fake.company()} Settings"
        phone = generate_phone()
        address = fake.address().replace('\n', ' ')
        website = fake.url()
        email = fake.email()
        logo_url = fake.image_url()
        description = fake.text(max_nb_chars=200)
        conn.execute(text(f"""
        INSERT INTO gym_settings (id, branch_id, gym_id, name, phone, address, website, email, logo_url, description, created_at)
        VALUES ('{gs_id}', '{branch_id}', '{gym_id}', '{name}', '{phone}', '{address}', '{website}', '{email}', '{logo_url}', '{description}', '{datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
        """))
    return gs_ids

if __name__ == "__main__":
    create_mock_data()