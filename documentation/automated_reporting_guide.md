# Lead Performance Reporting System Documentation

## What is this system?

This is an automated reporting system that creates beautiful, data-rich reports about your gym's lead and call performance. It collects and analyzes information from your database, then generates professionally formatted reports that show:

- How many leads you acquired during the period
- Your lead-to-member conversion rates
- Call performance metrics (pickup rates, interest levels)
- Staff performance comparisons
- Time-of-day effectiveness analysis
- Week-over-week trend comparisons (for weekly reports)

The system works completely automatically once set up. Reports are delivered directly to specified recipients via email or Slack at scheduled times. You can receive daily reports (every morning showing yesterday's performance) and weekly reports (every Monday summarizing last week's performance).

The reports contain visual indicators showing improvements or declines in key metrics, making it easy to spot trends at a glance. All of this happens without any manual work - just set it up once and enjoy insights delivered to your inbox automatically!

## How do I start using it?

### Step 1: Run the database migration

First, we need to tell the database about our new reporting system by running the Alembic migration that creates all necessary tables:

```bash
cd /Users/saivishwasgooty/Documents/incubator/reps-ai-dashboard-backend
alembic upgrade head
```

This migration (`76181331d9e4_add_reporting_system_tables.py`) creates three important tables in your Neon database:

1. **report_templates** - Stores HTML templates that control how reports look
2. **report_subscriptions** - Records who should receive which reports and when
3. **report_deliveries** - Maintains a history of all reports generated and their delivery status

Once the migration completes successfully, your database will be ready to support the reporting system. You don't need to create these tables manually - the migration handles everything automatically.

### Step 2: Create a subscription to get reports

After the database is ready, you need to create a subscription to define who receives reports and when. This is done through the API:

1. **Open your API testing tool** (like Postman, Insomnia, or cURL)
2. **Authenticate** with admin credentials (reports require admin access)
3. **Send a POST request** to: `http://your-server/api/analytics/reporting/subscriptions`
4. **Include this information** in the JSON body (replace with your real UUIDs):

```json
{
  "branch_id": "550e8400-e29b-41d4-a716-446655440000",
  "gym_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "report_type": "daily",
  "delivery_method": "email",
  "recipients": ["your-email@example.com"],
  "delivery_time": "09:00",
  "created_by": "550e8400-e29b-41d4-a716-446655440001"
}
```

**For weekly reports**, use these settings instead:

```json
"report_type": "weekly",
"delivery_time": "08:00",
"delivery_days": ["Monday"]
```

**What each field does:**
- `branch_id`: The branch this report covers (must exist in branches table)
- `gym_id`: The gym this report covers (must exist in gyms table)
- `report_type`: Whether it's "daily" or "weekly" 
- `delivery_method`: How to deliver - "email" or "slack"
- `recipients`: Email addresses or webhook URLs that should receive reports
- `delivery_time`: When to send in 24-hour format (HH:MM)
- `delivery_days`: For weekly reports, which day(s) to send
- `created_by`: User ID of the admin creating this subscription (must exist in users table)

If the request is successful, you'll receive a response with the created subscription details including an ID.

### Step 3: Generate a report right now (optional)

While the system will automatically generate reports based on your subscriptions, you might want to see a report immediately to verify everything works or to get insights right away. Here's how:

1. **Make sure you have data for the period** you want to report on (lead and call data)
2. **Send a POST request** to: `http://your-server/api/analytics/reporting/generate`
3. **Include this information** in the request body:

```json
{
  "report_type": "daily",
  "branch_id": "550e8400-e29b-41d4-a716-446655440000",
  "gym_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "recipients": ["your-email@example.com"],
  "date": "2025-04-25"  // Optional: specific date for the report, defaults to yesterday
}
```

**What happens when you trigger this:**
1. The system immediately generates a report for the specified branch/gym
2. It analyzes all lead and call data for the requested period
3. The report is formatted using the default template (or a custom one if specified)
4. If recipients are provided, it sends the report right away
5. A delivery record is created in the database that you can query later

**Response:** You'll receive a JSON response with a `delivery_id` that you can use to check the status or retrieve the report data later.

For weekly reports, the request is similar but with a date range:

```json
{
  "report_type": "weekly",
  "branch_id": "550e8400-e29b-41d4-a716-446655440000",
  "gym_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "recipients": ["your-email@example.com"],
  "start_date": "2025-04-14",  // Optional: start date for weekly period
  "end_date": "2025-04-20"     // Optional: end date for weekly period
}
```

### Step 4: Make sure the scheduled tasks are running

The reporting system relies on background tasks to automatically generate and deliver reports. These tasks are managed by Celery, which needs to be running correctly. There are two components you need to start:

#### 1. Celery Worker (processes the tasks)

Open a terminal and run:

```bash
cd /Users/saivishwasgooty/Documents/incubator/reps-ai-dashboard-backend
celery -A backend.celery_app worker -Q reports_tasks -l info
```

This command starts a dedicated worker that handles report generation and delivery tasks. The `-Q reports_tasks` option tells the worker to focus on report-related tasks, ensuring they're processed efficiently.

You should see output confirming the worker has started successfully. Keep this terminal window open.

#### 2. Celery Beat (schedules the tasks)

Open another terminal window and run:

```bash
cd /Users/saivishwasgooty/Documents/incubator/reps-ai-dashboard-backend
celery -A backend.celery_app beat -l info
```

This starts the scheduler that triggers report tasks at the appropriate times. It checks:
- Every minute for reports that need to be generated based on subscriptions
- Every 5 minutes for pending reports that need to be processed and delivered
- At 1:00 AM daily for daily report generation
- At 2:00 AM on Mondays for weekly report generation

You should see periodic output showing scheduled tasks being triggered.

**For production environments:** In production, you would typically run these as background services using something like Supervisor, systemd, or PM2. For example:

```bash
# Using PM2
pm2 start "celery -A backend.celery_app worker -Q reports_tasks -l info" --name "reports-worker"
pm2 start "celery -A backend.celery_app beat -l info" --name "celery-beat"
```

**Verifying tasks are working:** Check the console output of the Celery worker to confirm tasks are being processed. You should see log messages about checking for reports, processing reports, etc.

## What's in the reports?

The automated reports contain rich data visualizations and metrics that give you a complete picture of your gym's lead generation and conversion performance. Here's a detailed breakdown of what you'll find:

### Daily Reports

Daily reports provide a snapshot of the previous day's performance and are typically delivered each morning. They include:

#### Executive Summary
- A headline summary capturing key performance metrics at a glance
- Visual highlight of the most important trends or changes

#### Lead Performance Metrics
- Total lead count for the day
- Breakdown by lead status (new, contacted, qualified, converted, lost)
- Conversion percentages at each stage
- Lead sources and their effectiveness
- Lead quality scores

#### Call Performance Analytics
- Total calls made and received
- Answered vs. missed call rates
- Average call duration
- Call outcome distribution (interested, very interested, not interested, etc.)
- Interest level metrics

#### Time of Day Analysis
- Peak hours for lead generation
- Most effective calling times
- Response rate by hour
- Conversion rate by time of day

#### Staff Performance (if multiple staff members)
- Call volumes per staff member
- Pickup rates by staff member
- Conversion success by staff member
- Average call quality scores

### Weekly Reports

Weekly reports provide a comprehensive view of the entire week's performance with trend analysis and are typically delivered on Monday mornings. They include:

#### Executive Summary
- Week's headline performance metrics
- Week-over-week comparison highlights
- Key areas of improvement or concern

#### Comparative Performance Metrics
- This week vs. previous week metrics
- Visual trend indicators (↑/↓) showing direction of change
- Percentage changes in key metrics
- Historical trend charts

#### Lead Funnel Analysis
- Complete funnel visualization from new leads to conversions
- Drop-off rates between funnel stages
- Week-over-week funnel efficiency comparison
- Conversion velocity metrics (time to convert)

#### Detailed Staff Performance Comparison
- Staff leaderboard based on key metrics
- Individual improvement/decline indicators
- Staff conversion rate comparisons
- Call quality evaluations

#### Strategic Insights
- Recommended focus areas based on data
- Underperforming metrics requiring attention
- Successful strategies worth continuing
- Projected performance based on trends

Both report types include professional formatting with your gym's branding, clear data visualizations, and color-coded indicators to quickly identify positive and negative trends.

## How do I know it's working?

After setting up the reporting system, you'll want to verify that everything is functioning correctly. Here are several ways to confirm the system is working properly:

### 1. Check Your Email Inbox

The most direct way to verify the system is working is to check if reports are arriving in your inbox:
- **For daily reports**: Check your email after the scheduled delivery time (e.g., 9:00 AM)
- **For weekly reports**: Check on the scheduled day (e.g., Monday morning)
- **For on-demand reports**: Check immediately after triggering generation

Look for:
- Emails with the subject line containing "Daily Lead Performance Report" or "Weekly Lead Performance Report"
- Professionally formatted HTML content with metrics and visualizations
- Correct data for the specified time period

Make sure to check your spam/junk folder if you don't see the reports in your inbox.

### 2. Monitor Slack Notifications

If you configured Slack as a delivery method:
- Check the configured Slack channel after the scheduled delivery time
- Look for messages containing the report summary
- Check that embedded links to full reports work correctly
- Verify that metrics in the summary match your expectations

### 3. Check the Database Directly

For a definitive verification, you can query the database directly:

```sql
SELECT * FROM report_deliveries ORDER BY created_at DESC LIMIT 10;
```

This will show the 10 most recent report deliveries with their:
- Delivery status ('pending', 'sent', 'failed')
- Timestamp of generation and delivery
- Recipients
- Error messages (if any)

### 4. Use the API to Check Status

The most user-friendly way to check status is through the API:

1. Send a GET request to: `http://your-server/api/analytics/reporting/deliveries`
2. Filter by status if needed: `http://your-server/api/analytics/reporting/deliveries?status=sent`
3. Filter by date range: `http://your-server/api/analytics/reporting/deliveries?start_date=2025-04-20&end_date=2025-04-26`
4. Look for a specific delivery: `http://your-server/api/analytics/reporting/deliveries/{delivery_id}`

The response will include detailed information about each delivery, including timestamps, status, and any error messages.

### 5. Monitor Celery Task Logs

For real-time monitoring of the report generation process:

1. Watch the Celery worker terminal output
2. Look for log messages about:
   - Checking for scheduled reports
   - Processing pending reports
   - Successful or failed deliveries

### 6. Verify Report Generation Process

To ensure the full process is working correctly:

1. Create a test subscription with a delivery time a few minutes in the future
2. Watch the Celery logs at that time to see the scheduled task trigger
3. Confirm the report is generated and sent
4. Check the delivery status through the API
5. Verify receipt in email or Slack

## What files were added and what do they do?

The reporting system comprises 33 carefully designed files that work together to create a cohesive, automated reporting solution. Here's a detailed breakdown of what each file does:

### Database Layer

#### Database Models
- `/backend/db/models/reporting/report_models.py`: 
  - Defines the three main database tables: `ReportTemplate`, `ReportSubscription`, and `ReportDelivery`
  - Includes data conversion methods (`to_dict`) for serializing database objects
  - Sets up relationships between tables (like templates linked to subscriptions)
  - Includes proper typing and documentation for each model

#### Database Migration
- `/alembic/versions/76181331d9e4_add_reporting_system_tables.py`: 
  - Creates all necessary database tables with proper constraints
  - Sets up foreign key relationships to existing tables (branches, gyms, users)
  - Adds indexes for optimized query performance
  - Includes downgrade function to cleanly remove tables if needed

#### Database Repository Interface
- `/backend/db/repositories/reporting/interface.py`: 
  - Defines the abstract `ReportRepository` interface
  - Specifies all methods needed for database operations
  - Enforces type checking for repository implementations
  - Ensures consistent behavior across different repository implementations

#### PostgreSQL Repository Implementation
- `/backend/db/repositories/reporting/implementations/postgres_report_repository.py`: 
  - Implements the repository interface for PostgreSQL/Neon
  - Handles create, read, update, delete operations for all report models
  - Includes proper error handling and transaction management
  - Uses caching for frequently accessed data to improve performance

### Service Layer

#### Reporting Service Interface
- `/backend/services/reporting/interface.py`: 
  - Defines the high-level operations the reporting system can perform
  - Separates concerns between business logic and data access
  - Provides clear method signatures with type hints
  - Acts as a contract for any reporting service implementation

#### Reporting Service Implementation
- `/backend/services/reporting/implementation.py`: 
  - Contains the core business logic for report generation
  - Handles data collection, analysis, and report formatting
  - Coordinates between repositories, email service, and notification service
  - Implements scheduling logic for determining when reports should run

#### Service Factory
- `/backend/services/reporting/factory.py`: 
  - Creates properly configured reporting service instances
  - Handles dependency injection for repositories and other services
  - Simplifies service instantiation throughout the application
  - Allows for easy testing with mock dependencies

### Email and Notification Services

#### Email Service
- `/backend/services/email/interface.py`: 
  - Defines the contract for sending emails
  - Specifies required methods and parameters
  - Ensures email service implementations are interchangeable

- `/backend/services/email/implementation.py`: 
  - Implements email delivery functionality
  - Handles HTML email formatting
  - Manages SMTP connections and error handling
  - Includes retry logic for failed deliveries

- `/backend/services/email/factory.py`: 
  - Creates email service instances with proper configuration
  - Reads settings from application configuration

#### Notification Service (for Slack/webhooks)
- `/backend/services/notification/interface.py`: 
  - Defines methods for sending webhook notifications
  - Establishes parameter requirements for notifications

- `/backend/services/notification/implementation.py`: 
  - Handles webhook delivery to services like Slack
  - Formats payloads appropriately for different platforms
  - Manages HTTP connections and error handling
  - Includes specialized formatters for Slack's Block Kit

- `/backend/services/notification/factory.py`: 
  - Creates notification service instances with proper configuration
  - Handles necessary dependencies

### API Layer

#### API Endpoints
- `/app/routes/analytics/reporting.py`: 
  - Defines all REST API endpoints for the reporting system
  - Handles authentication and authorization for report access
  - Processes incoming requests and returns appropriate responses
  - Includes endpoints for templates, subscriptions, and report generation

#### API Schemas
- `/app/schemas/analytics/report_schemas.py`: 
  - Defines data validation for API requests
  - Specifies response formats for consistency
  - Handles data transformation between API and service layers
  - Includes documentation for OpenAPI/Swagger

### Report Templates

#### HTML Templates
- `/templates/reports/daily_report.html`: 
  - Contains the HTML structure for daily reports
  - Includes responsive styling for proper display on all devices
  - Uses template variables for dynamic content insertion
  - Features professional design with data visualizations

- `/templates/reports/weekly_report.html`: 
  - Contains the HTML structure for weekly reports
  - Includes trend indicators and comparative visualizations
  - Uses conditional formatting to highlight improvements/declines
  - Features collapsible sections for detailed metrics

### Automated Task System

#### Task Definitions
- `/backend/tasks/reports.py`: 
  - Defines all Celery tasks for report processing
  - Handles scheduled report checking
  - Manages report generation and delivery
  - Includes proper error handling and logging

#### Task Scheduler
- `/backend/tasks/reporting_scheduler.py`: 
  - Registers reporting tasks with the Celery beat scheduler
  - Sets up periodic task schedules
  - Ensures tasks run at appropriate times
  - Configures task routing for optimal processing

### Documentation
- `/documentation/automated_reporting_guide.md`: 
  - This comprehensive guide you're reading now!
  - Explains how to use and troubleshoot the reporting system
  - Provides examples and usage scenarios
  - Answers common questions about the system

## API Endpoints Guide

The reporting system provides a comprehensive set of API endpoints to manage templates, subscriptions, and report generation. All endpoints are available under the `/api/analytics/reporting` base path. Here's a detailed guide to each endpoint:

### Report Templates

| Method | Endpoint | Description | Example Request | Response |
|--------|----------|-------------|----------------|----------|
| `GET` | `/api/analytics/reporting/templates` | List all available report templates | `GET /api/analytics/reporting/templates?template_type=html` | Array of template objects |
| `POST` | `/api/analytics/reporting/templates` | Create a new report template | `POST` with template name, type, and content | Newly created template object |
| `GET` | `/api/analytics/reporting/templates/{id}` | Get a specific template by ID | `GET /api/analytics/reporting/templates/66666666-6666-6666-6666-666666666666` | Single template object |
| `PUT` | `/api/analytics/reporting/templates/{id}` | Update an existing template | `PUT` with updated template fields | Updated template object |
| `DELETE` | `/api/analytics/reporting/templates/{id}` | Delete a template | `DELETE /api/analytics/reporting/templates/66666666-6666-6666-6666-666666666666` | Success confirmation |

#### Query Parameters for Templates

- `template_type`: Filter by type (e.g., "html", "text")
- `sort_by`: Sort results (e.g., "created_at", "name")
- `sort_direction`: Sort order ("asc" or "desc")
- `limit` & `offset`: Pagination controls

### Report Subscriptions

| Method | Endpoint | Description | Example Request | Response |
|--------|----------|-------------|----------------|----------|
| `GET` | `/api/analytics/reporting/subscriptions` | List all report subscriptions | `GET /api/analytics/reporting/subscriptions?branch_id=22222222-2222-2222-2222-222222222222` | Array of subscription objects |
| `POST` | `/api/analytics/reporting/subscriptions` | Create a new subscription | `POST` with subscription details | Newly created subscription |
| `GET` | `/api/analytics/reporting/subscriptions/{id}` | Get a specific subscription | `GET /api/analytics/reporting/subscriptions/77777777-7777-7777-7777-777777777777` | Single subscription object |
| `PUT` | `/api/analytics/reporting/subscriptions/{id}` | Update a subscription | `PUT` with updated fields | Updated subscription object |
| `PATCH` | `/api/analytics/reporting/subscriptions/{id}/activate` | Activate a subscription | `PATCH /api/analytics/reporting/subscriptions/77777777-7777-7777-7777-777777777777/activate` | Updated status |
| `PATCH` | `/api/analytics/reporting/subscriptions/{id}/deactivate` | Deactivate a subscription | `PATCH /api/analytics/reporting/subscriptions/77777777-7777-7777-7777-777777777777/deactivate` | Updated status |
| `DELETE` | `/api/analytics/reporting/subscriptions/{id}` | Delete a subscription | `DELETE /api/analytics/reporting/subscriptions/77777777-7777-7777-7777-777777777777` | Success confirmation |

#### Query Parameters for Subscriptions

- `branch_id`: Filter by branch
- `gym_id`: Filter by gym
- `report_type`: Filter by type ("daily", "weekly")
- `is_active`: Filter by active status (true/false)
- `created_by`: Filter by creator
- `sort_by` & `sort_direction`: Sorting controls
- `limit` & `offset`: Pagination controls

### Report Generation and Delivery

| Method | Endpoint | Description | Example Request | Response |
|--------|----------|-------------|----------------|----------|
| `POST` | `/api/analytics/reporting/generate` | Generate a report on demand | `POST` with report type, branch ID, and optional recipients | Generated report delivery object |
| `POST` | `/api/analytics/reporting/send` | Send an existing report | `POST` with delivery ID and recipients | Updated delivery status |
| `GET` | `/api/analytics/reporting/deliveries` | List all report deliveries | `GET /api/analytics/reporting/deliveries?status=sent&sort_by=created_at&sort_direction=desc` | Array of delivery objects |
| `GET` | `/api/analytics/reporting/deliveries/{id}` | Get a specific delivery | `GET /api/analytics/reporting/deliveries/88888888-8888-8888-8888-888888888888` | Single delivery object with report data |
| `GET` | `/api/analytics/reporting/deliveries/{id}/html` | Get HTML version of report | `GET /api/analytics/reporting/deliveries/88888888-8888-8888-8888-888888888888/html` | HTML content of the report |
| `POST` | `/api/analytics/reporting/deliveries/{id}/retry` | Retry a failed delivery | `POST /api/analytics/reporting/deliveries/88888888-8888-8888-8888-888888888888/retry` | Updated delivery status |

#### Query Parameters for Deliveries

- `branch_id`: Filter by branch
- `gym_id`: Filter by gym
- `report_type`: Filter by type ("daily", "weekly")
- `status`: Filter by status ("pending", "sent", "failed")
- `start_date` & `end_date`: Filter by delivery date range
- `sort_by` & `sort_direction`: Sorting controls
- `limit` & `offset`: Pagination controls
- `include_data`: Whether to include full report data in responses (true/false)

### Authentication

All endpoints require authentication with a valid JWT token as a Bearer token in the Authorization header:

```
Authorization: Bearer your-jwt-token
```

For most operations, the user must have admin privileges. Regular users can only access deliveries for their own branch/gym.

## Frequently Asked Questions

### How do I change how the reports look?
You can create a custom template through the API:

1. Send a POST request to: `http://your-server/api/analytics/reporting/templates`
2. Include your custom HTML template

### Can I send reports to Slack?
Yes! When creating a subscription, set:
```json
"delivery_method": "slack",
"recipients": ["https://hooks.slack.com/services/YOUR_WEBHOOK_URL"]
```

### What if a report fails to send?
The system will automatically retry failed deliveries. You can check the status using the API:
```
GET /api/analytics/reporting/deliveries?status=failed
```

### How do I change when reports are sent?
Update your subscription with:
```json
"delivery_time": "17:00"  // For 5:00 PM
```

### Can I generate reports for a specific date range?
Yes! Use the `generate` endpoint with:
```json
{
  "report_type": "daily",
  "date": "2025-04-25"
}
```
Or for weekly:
```json
{
  "report_type": "weekly",
  "start_date": "2025-04-14",
  "end_date": "2025-04-20"
}
```

### What data is used in the reports?
The system uses the data already in your database about:
- Leads (potential gym members)
- Their current status (new, contacted, qualified, converted)
- Calls made to leads
- Call outcomes and durations

### Can I see a report without sending emails?
Yes! Generate a report but leave out the recipients:
```
POST /api/analytics/reporting/generate
```
Then get the delivery record:
```
GET /api/analytics/reporting/deliveries
```
The report data will be included in the response.

## Step-by-Step Example

Here's how to create daily reports for your gym:

1. **Add database tables**:
   ```bash
   alembic upgrade head
   ```

2. **Create a subscription**:
   ```http
   POST /api/analytics/reporting/subscriptions
   {
     "branch_id": "your-branch-id",
     "gym_id": "your-gym-id",
     "report_type": "daily",
     "delivery_method": "email",
     "recipients": ["manager@yourgym.com"],
     "delivery_time": "08:00",
     "created_by": "your-user-id"
   }
   ```

3. **Start the scheduler**:
   ```bash
   celery -A backend.celery_app worker -Q reports_tasks -l info
   celery -A backend.celery_app beat -l info
   ```

4. **Generate a test report**:
   ```http
   POST /api/analytics/reporting/generate
   {
     "report_type": "daily",
     "branch_id": "your-branch-id",
     "gym_id": "your-gym-id",
     "recipients": ["manager@yourgym.com"]
   }
   ```

5. **Check your email** for the beautiful report!

## Data Format and Table Structure

The reporting system relies on certain data in your database. Here's what each table needs to have:

### Existing Tables Used by the Reporting System

#### `leads` Table
This table contains information about potential gym members:

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| id | UUID | Unique identifier | 11111111-1111-1111-1111-111111111111 |
| branch_id | UUID | Branch ID | 22222222-2222-2222-2222-222222222222 |
| gym_id | UUID | Gym ID | 33333333-3333-3333-3333-333333333333 |
| first_name | String | Lead's first name | John |
| last_name | String | Lead's last name | Doe |
| phone | String | Phone number | +15551234567 |
| email | String | Email address | john@example.com |
| lead_status | String | Current status | new, contacted, qualified, converted, lost |
| created_at | DateTime | When created | 2025-04-25 10:30:00 |
| updated_at | DateTime | When updated | 2025-04-25 15:45:00 |

#### `call_logs` Table
This table tracks calls made to leads:

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| id | UUID | Unique identifier | 44444444-4444-4444-4444-444444444444 |
| lead_id | UUID | Related lead | 11111111-1111-1111-1111-111111111111 |
| branch_id | UUID | Branch ID | 22222222-2222-2222-2222-222222222222 |
| gym_id | UUID | Gym ID | 33333333-3333-3333-3333-333333333333 |
| user_id | UUID | Staff who made call | 55555555-5555-5555-5555-555555555555 |
| direction | String | Call direction | outbound |
| status | String | Call status | completed, missed, failed |
| outcome | String | Call outcome | interested, not_interested, wrong_number |
| duration | Integer | Duration in seconds | 120 |
| created_at | DateTime | When call happened | 2025-04-25 11:30:00 |
| notes | Text | Call notes | Customer asked about pricing |

### New Tables Created by the Reporting System

#### `report_templates` Table
Stores HTML templates for report formatting:

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| id | UUID | Unique identifier | 66666666-6666-6666-6666-666666666666 |
| name | String | Template name | Custom Daily Report |
| description | Text | Description | Report template with company branding |
| template_type | String | Type of template | html |
| template_content | Text | HTML content | `<!DOCTYPE html><html>...</html>` |
| created_at | DateTime | When created | 2025-04-25 09:00:00 |
| updated_at | DateTime | When updated | 2025-04-25 09:00:00 |

#### `report_subscriptions` Table
Manages who gets what reports and when:

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| id | UUID | Unique identifier | 77777777-7777-7777-7777-777777777777 |
| branch_id | UUID | Branch ID | 22222222-2222-2222-2222-222222222222 |
| gym_id | UUID | Gym ID | 33333333-3333-3333-3333-333333333333 |
| report_type | String | Type of report | daily, weekly |
| template_id | UUID | Template ID (optional) | 66666666-6666-6666-6666-666666666666 |
| is_active | Boolean | Whether active | true |
| delivery_method | String | How to deliver | email, slack |
| recipients | JSON | Who receives it | ["manager@example.com"] |
| delivery_time | String | When to deliver | 09:00 |
| delivery_days | JSON | Days to deliver (weekly) | ["Monday"] |
| created_by | UUID | User who created | 55555555-5555-5555-5555-555555555555 |
| created_at | DateTime | When created | 2025-04-25 09:00:00 |
| updated_at | DateTime | When updated | 2025-04-25 09:00:00 |

#### `report_deliveries` Table
Tracks report generation and delivery history:

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| id | UUID | Unique identifier | 88888888-8888-8888-8888-888888888888 |
| report_type | String | Type of report | daily, weekly |
| branch_id | UUID | Branch ID | 22222222-2222-2222-2222-222222222222 |
| gym_id | UUID | Gym ID | 33333333-3333-3333-3333-333333333333 |
| template_id | UUID | Template ID (optional) | 66666666-6666-6666-6666-666666666666 |
| recipients | JSON | Who receives it | ["manager@example.com"] |
| report_data | JSON | Report data cache | {...} |
| report_period_start | DateTime | Start of period | 2025-04-25 00:00:00 |
| report_period_end | DateTime | End of period | 2025-04-25 23:59:59 |
| delivery_status | String | Delivery status | pending, sent, failed |
| delivery_time | DateTime | When delivered | 2025-04-26 09:00:00 |
| error_message | Text | Error if failed | SMTP connection refused |
| created_at | DateTime | When created | 2025-04-26 09:00:00 |
| updated_at | DateTime | When updated | 2025-04-26 09:00:00 |

### How to Add Sample Data

To insert sample data into these tables:

#### 1. Create a Template:
```sql
INSERT INTO report_templates (id, name, description, template_type, template_content, created_at, updated_at)
VALUES (
  '66666666-6666-6666-6666-666666666666', 
  'Custom Daily Report', 
  'Report template with company branding', 
  'html',
  '<!DOCTYPE html><html><head><title>Daily Report</title></head><body><h1>Daily Report</h1></body></html>',
  NOW(), 
  NOW()
);
```

#### 2. Create a Subscription:
```sql
INSERT INTO report_subscriptions (id, branch_id, gym_id, report_type, template_id, is_active, delivery_method, recipients, delivery_time, delivery_days, created_by, created_at, updated_at)
VALUES (
  '77777777-7777-7777-7777-777777777777',
  '22222222-2222-2222-2222-222222222222',
  '33333333-3333-3333-3333-333333333333',
  'daily',
  '66666666-6666-6666-6666-666666666666',
  true,
  'email',
  '["manager@example.com"]',
  '09:00',
  NULL,
  '55555555-5555-5555-5555-555555555555',
  NOW(),
  NOW()
);
```

#### 3. For Testing, Create a Delivery Record:
```sql
INSERT INTO report_deliveries (id, report_type, branch_id, gym_id, template_id, recipients, report_period_start, report_period_end, delivery_status, created_at, updated_at)
VALUES (
  '88888888-8888-8888-8888-888888888888',
  'daily',
  '22222222-2222-2222-2222-222222222222',
  '33333333-3333-3333-3333-333333333333',
  '66666666-6666-6666-6666-666666666666',
  '["manager@example.com"]',
  '2025-04-25 00:00:00',
  '2025-04-25 23:59:59',
  'pending',
  NOW(),
  NOW()
);
```

### Where to Store This Data

All of this data is stored in your existing PostgreSQL database (Neon). The database migration automatically creates the new tables when you run `alembic upgrade head`.

The reporting system uses your existing lead and call data to generate reports, and it stores templates, subscriptions, and delivery history in the new tables.

## Troubleshooting

### Reports aren't being generated
- Check that Celery worker and beat are running
- Make sure your subscription is active
- Check logs for any errors

### Email reports aren't arriving
- Verify your email settings in application config
- Check spam/junk folders
- Look at the delivery status in the API

### Report data looks empty or wrong
- Make sure you have lead and call data for the time period
- Check that your branch_id and gym_id are correct
- Manually generate a report to see the specific issue

### Need more help?
Check the logs in your application for detailed error messages.

---

I hope this guide helps you enjoy your new automated reporting system! Now you'll always know how your gym is doing, with beautiful reports delivered right to your inbox.
