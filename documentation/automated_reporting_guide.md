# Lead Performance Reporting System Documentation

## What is this system?

This is a magical system that creates beautiful reports about how your gym is doing! It collects information about leads (potential gym members) and calls, then creates nice-looking reports that show:

- How many leads you got
- How many became actual members
- How successful your calls were
- Which staff members are doing the best job
- What time of day gets the best results

These reports automatically arrive in your email or Slack every day or every week!

## How do I start using it?

### Step 1: Run the database migration

First, we need to tell the database about our new reporting system:

```bash
cd /Users/saivishwasgooty/Documents/incubator/reps-ai-dashboard-backend
alembic upgrade head
```

This creates special tables in the database to store:
- Report templates (how the reports look)
- Report subscriptions (who gets which reports and when)
- Report delivery records (a history of what reports were sent)

### Step 2: Create a subscription to get reports

You can create a subscription through the API:

1. Open your API testing tool (like Postman)
2. Send a POST request to: `http://your-server/api/analytics/reporting/subscriptions`
3. Include this information (replace with your real IDs):

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

For weekly reports, add this:

```json
"report_type": "weekly",
"delivery_days": ["Monday"]
```

### Step 3: Generate a report right now (optional)

If you want to see a report immediately:

1. Send a POST request to: `http://your-server/api/analytics/reporting/generate`
2. Include this information:

```json
{
  "report_type": "daily",
  "branch_id": "550e8400-e29b-41d4-a716-446655440000",
  "gym_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "recipients": ["your-email@example.com"]
}
```

### Step 4: Make sure the scheduled tasks are running

The system uses Celery to run tasks automatically. Make sure the Celery worker and beat scheduler are running:

```bash
# Start the Celery worker for report tasks
celery -A backend.celery_app worker -Q reports_tasks -l info

# Start the Celery beat scheduler
celery -A backend.celery_app beat -l info
```

## What's in the reports?

### Daily Reports
- Yesterday's performance
- Lead counts by status
- Call success rates
- Interest breakdowns
- Time-of-day analysis

### Weekly Reports
- Last week's performance
- Comparisons to the previous week
- Lead funnel progression
- Staff performance comparison
- Trend indicators showing improvement or decline

## How do I know it's working?

1. **Check your email**: You should receive reports at the time you specified
2. **Check Slack**: If you set up Slack delivery, check your Slack channel
3. **Check the database**: Look at the `report_deliveries` table to see delivery status
4. **API Check**: Send a GET request to `http://your-server/api/analytics/reporting/deliveries` to see all report deliveries

## What files were added and what do they do?

### Database Models
- `/backend/db/models/reporting/report_models.py`: Defines database tables for storing templates, subscriptions, and delivery history

### Database Repository
- `/backend/db/repositories/reporting/interface.py`: Defines what operations can be performed on report data
- `/backend/db/repositories/reporting/implementations/postgres_report_repository.py`: Handles all database operations for reports

### Service Layer
- `/backend/services/reporting/interface.py`: Defines what the reporting service can do
- `/backend/services/reporting/implementation.py`: Contains all the logic for generating and sending reports
- `/backend/services/reporting/factory.py`: Creates new reporting service instances

### Email and Notifications
- `/backend/services/email/interface.py`: Defines how emails can be sent
- `/backend/services/email/implementation.py`: Handles sending emails with reports
- `/backend/services/email/factory.py`: Creates email service instances
- `/backend/services/notification/interface.py`: Defines how notifications can be sent
- `/backend/services/notification/implementation.py`: Handles sending reports to webhooks like Slack
- `/backend/services/notification/factory.py`: Creates notification service instances

### API Endpoints
- `/app/routes/analytics/reporting.py`: All the API endpoints for managing reports
- `/app/schemas/analytics/report_schemas.py`: Defines the format of API requests and responses

### Report Templates
- `/templates/reports/daily_report.html`: Beautiful template for daily reports
- `/templates/reports/weekly_report.html`: Beautiful template for weekly reports with trend indicators

### Automated Tasks
- `/backend/tasks/reports.py`: Tasks that run automatically to generate and send reports
- `/backend/tasks/reporting_scheduler.py`: Sets up when tasks should run

### Database Migration
- `/alembic/versions/76181331d9e4_add_reporting_system_tables.py`: Adds necessary tables to the database

## API Endpoints Guide

Here are all the API endpoints you can use:

### Templates
- `GET /api/analytics/reporting/templates`: List all templates
- `POST /api/analytics/reporting/templates`: Create a new template
- `GET /api/analytics/reporting/templates/{id}`: Get a specific template
- `PUT /api/analytics/reporting/templates/{id}`: Update a template
- `DELETE /api/analytics/reporting/templates/{id}`: Delete a template

### Subscriptions
- `GET /api/analytics/reporting/subscriptions`: List all subscriptions
- `POST /api/analytics/reporting/subscriptions`: Create a new subscription
- `GET /api/analytics/reporting/subscriptions/{id}`: Get a specific subscription
- `PUT /api/analytics/reporting/subscriptions/{id}`: Update a subscription
- `DELETE /api/analytics/reporting/subscriptions/{id}`: Delete a subscription

### Reports
- `POST /api/analytics/reporting/generate`: Generate a report on demand
- `POST /api/analytics/reporting/send`: Send an existing report
- `GET /api/analytics/reporting/deliveries`: List report deliveries
- `GET /api/analytics/reporting/deliveries/{id}`: Get a specific delivery

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
