# Fitness Gym CRM API Documentation

This document outlines the available API endpoints for the fitness gym CRM system, focusing on leads and calls management.

## Leads API

### Base URL
`/leads`

### Endpoints

#### 1. Get All Leads (Paginated)
```
GET /leads/
```

**Query Parameters:**
- `status`: Filter by lead status (`new`, `contacted`, `qualified`, `converted`, `lost`)
- `branch_id`: Filter by branch UUID
- `search`: Search text in lead fields
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 10, max: 100)
- `sort_by`: Field to sort by
- `sort_order`: `asc` or `desc`

**Response:**
```json
{
  "data": [
    {
      "id": "uuid-string",
      "first_name": "John",
      "last_name": "Doe",
      "phone": "+1234567890",
      "email": "john.doe@example.com",
      "status": "qualified",
      "source": "website",
      "branch_id": "uuid-string",
      "branch_name": "Downtown Fitness",
      "notes": "Interested in personal training",
      "interest": "Personal Training",
      "interest_location": "Downtown",
      "last_conversation_summary": "Discussed membership options",
      "score": 0.85,
      "call_count": 3,
      "last_called": "2023-04-05T15:30:00Z",
      "created_at": "2023-04-01T10:00:00Z",
      "updated_at": "2023-04-05T15:30:00Z",
      "appointment_date": "2023-04-10T14:00:00Z",
      "tags": [
        {
          "id": "uuid-string",
          "name": "VIP",
          "color": "#FF5733"
        }
      ]
    }
  ],
  "pagination": {
    "total": 45,
    "page": 1,
    "limit": 10,
    "pages": 5
  }
}
```

**Usage Example:**
Fetch qualified leads, sorted by creation date in descending order:
```
GET /leads/?status=qualified&sort_by=created_at&sort_order=desc&page=1&limit=20
```

#### 2. Get Leads by Branch
```
GET /leads/branch/{branch_id}
```

**Query Parameters:** Same as "Get All Leads"

**Response:** Same as "Get All Leads"

**Usage Example:**
Fetch all leads for a specific branch with search term:
```
GET /leads/branch/123e4567-e89b-12d3-a456-426614174000?search=fitness&page=1&limit=20
```

#### 3. Get Prioritized Leads
```
GET /leads/prioritized
```

**Query Parameters:**
- `count`: Number of leads to return (default: 10, max: 50)
- `qualification`: Filter by qualification level (`hot`, `cold`, `neutral`)
- `exclude_leads`: Comma-separated list of lead IDs to exclude

**Response:**
Array of lead objects (same structure as in "Get All Leads" data array)

**Usage Example:**
Get 20 hot leads, excluding specific leads:
```
GET /leads/prioritized?count=20&qualification=hot&exclude_leads=uuid1,uuid2,uuid3
```

#### 4. Get Lead Details
```
GET /leads/{id}
```

**Path Parameter:**
- `id`: Lead UUID

**Response:**
```json
{
  "id": "uuid-string",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "email": "john.doe@example.com",
  "status": "qualified",
  "source": "website",
  "branch_id": "uuid-string",
  "branch_name": "Downtown Fitness",
  "notes": "Interested in personal training",
  "interest": "Personal Training",
  "interest_location": "Downtown",
  "last_conversation_summary": "Discussed membership options",
  "score": 0.85,
  "call_count": 3,
  "last_called": "2023-04-05T15:30:00Z",
  "created_at": "2023-04-01T10:00:00Z",
  "updated_at": "2023-04-05T15:30:00Z",
  "appointment_date": "2023-04-10T14:00:00Z",
  "tags": [
    {
      "id": "uuid-string",
      "name": "VIP",
      "color": "#FF5733"
    }
  ],
  "assigned_to": {
    "id": "uuid-string",
    "first_name": "Jane",
    "last_name": "Smith"
  },
  "calls": [
    {
      "id": "uuid-string",
      "direction": "outbound",
      "status": "completed",
      "start_time": "2023-04-05T15:30:00Z",
      "duration": 300,
      "outcome": "appointment_booked",
      "sentiment": "positive",
      "summary": "Customer showed interest in premium membership"
    }
  ],
  "appointments": [
    {
      "id": "uuid-string",
      "type": "consultation",
      "date": "2023-04-10T14:00:00Z",
      "duration": 60,
      "status": "scheduled",
      "branch_name": "Downtown Fitness Center"
    }
  ]
}
```

**Usage Example:**
Fetch detailed information for a specific lead:
```
GET /leads/123e4567-e89b-12d3-a456-426614174000
```

#### 5. Create Lead
```
POST /leads/
```

**Request Body:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "email": "john.doe@example.com",
  "status": "new",
  "notes": "Interested in personal training",
  "interest": "Personal Training",
  "interest_location": "Downtown",
  "source": "website",
  "tags": ["uuid-tag1", "uuid-tag2"]
}
```

**Response:**
Lead object (same structure as in "Get Lead Details" but without calls/appointments)

**Usage Example:**
Create a new lead from a website form submission:
```
POST /leads/
{
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "email": "john.doe@example.com",
  "status": "new",
  "notes": "Filled out website form requesting information about classes",
  "interest": "Group Classes",
  "source": "website",
  "tags": []
}
```

#### 6. Update Lead
```
PUT /leads/{id}
```

**Path Parameter:**
- `id`: Lead UUID

**Request Body:**
```json
{
  "first_name": "John",
  "last_name": "Smith",
  "phone": "+1234567890",
  "email": "john.smith@example.com",
  "status": "qualified",
  "notes": "Updated notes",
  "interest": "Personal Training",
  "source": "website"
}
```
Note: All fields are optional; only include fields you want to update.

**Response:**
Updated lead object

**Usage Example:**
Update a lead's status and notes after a qualification call:
```
PUT /leads/123e4567-e89b-12d3-a456-426614174000
{
  "status": "qualified",
  "notes": "Lead is interested in premium membership, follow up next week"
}
```

#### 7. Add Tags to Lead
```
POST /leads/{id}/tags
```

**Path Parameter:**
- `id`: Lead UUID

**Request Body:**
```json
[
  "uuid-tag1",
  "uuid-tag2"
]
```

**Response:**
Lead object with updated tags

**Usage Example:**
Add VIP tag to a lead:
```
POST /leads/123e4567-e89b-12d3-a456-426614174000/tags
[
  "3fa85f64-5717-4562-b3fc-2c963f66afa6"
]
```

#### 8. Remove Tags from Lead
```
DELETE /leads/{id}/tags
```

**Path Parameter:**
- `id`: Lead UUID

**Request Body:**
```json
[
  "uuid-tag1",
  "uuid-tag2"
]
```

**Response:**
Lead object with updated tags

**Usage Example:**
Remove a tag from a lead:
```
DELETE /leads/123e4567-e89b-12d3-a456-426614174000/tags
[
  "3fa85f64-5717-4562-b3fc-2c963f66afa6"
]
```

#### 9. Delete Lead
```
DELETE /leads/{id}
```

**Path Parameter:**
- `id`: Lead UUID

**Response:**
```json
{
  "message": "Lead successfully deleted"
}
```

**Usage Example:**
Delete a lead that was created in error:
```
DELETE /leads/123e4567-e89b-12d3-a456-426614174000
```

## Calls API

### Base URL
`/calls`

### Endpoints

#### 1. Get All Calls (Paginated)
```
GET /calls/
```

**Query Parameters:**
- `lead_id`: Filter by lead UUID
- `campaign_id`: Filter by campaign UUID
- `direction`: Filter by call direction (`inbound`, `outbound`)
- `outcome`: Filter by call outcome
- `start_date`: Filter by start date (ISO format)
- `end_date`: Filter by end date (ISO format)
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 10, max: 100)

**Response:**
```json
{
  "calls": [
    {
      "id": "uuid-string",
      "lead_id": "uuid-string",
      "lead": {
        "id": "uuid-string",
        "first_name": "John",
        "last_name": "Doe",
        "phone": "+1234567890",
        "email": "john.doe@example.com"
      },
      "direction": "outbound",
      "status": "completed",
      "start_time": "2023-04-05T15:30:00Z",
      "end_time": "2023-04-05T15:35:00Z",
      "duration": 300,
      "outcome": "appointment_booked",
      "notes": "Successful call, lead was interested",
      "summary": "Discussed membership options and scheduled a visit",
      "sentiment": "positive",
      "recording_url": "https://example.com/recordings/call123.mp3",
      "created_at": "2023-04-05T15:25:00Z",
      "campaign_id": "uuid-string",
      "campaign_name": "April Promotion"
    }
  ],
  "pagination": {
    "total": 120,
    "page": 1,
    "page_size": 10,
    "pages": 12
  }
}
```

**Usage Example:**
Get all outbound calls with successful outcomes from the last week:
```
GET /calls/?direction=outbound&outcome=appointment_booked&start_date=2023-04-01&end_date=2023-04-07&page=1&limit=20
```

#### 2. Get Call Details
```
GET /calls/{call_id}
```

**Path Parameter:**
- `call_id`: Call UUID

**Response:**
```json
{
  "id": "uuid-string",
  "lead_id": "uuid-string",
  "lead": {
    "id": "uuid-string",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+1234567890",
    "email": "john.doe@example.com"
  },
  "direction": "outbound",
  "status": "completed",
  "start_time": "2023-04-05T15:30:00Z",
  "end_time": "2023-04-05T15:35:00Z",
  "duration": 300,
  "outcome": "appointment_booked",
  "notes": "Successful call, lead was interested",
  "summary": "Discussed membership options and scheduled a visit",
  "sentiment": "positive",
  "recording_url": "https://example.com/recordings/call123.mp3",
  "created_at": "2023-04-05T15:25:00Z",
  "campaign_id": "uuid-string",
  "campaign_name": "April Promotion",
  "transcript": [
    {
      "speaker": "agent",
      "text": "Hello, this is Fitness Gym calling. How are you today?",
      "timestamp": 0.0
    },
    {
      "speaker": "customer",
      "text": "I'm good, thanks for asking.",
      "timestamp": 3.5
    }
  ],
  "metrics": {
    "talk_ratio": 0.6,
    "interruptions": 0,
    "talk_speed": 145.2
  }
}
```

**Usage Example:**
Fetch detailed information about a specific call:
```
GET /calls/123e4567-e89b-12d3-a456-426614174000
```

#### 3. Create Call
```
POST /calls/
```

**Request Body:**
```json
{
  "lead_id": "uuid-string"
}
```

**Response:**
Confirmation of call creation

**Usage Example:**
Initiate a call to a specific lead:
```
POST /calls/
{
  "lead_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

#### 4. Update Call
```
PATCH /calls/{call_id}
```

**Path Parameter:**
- `call_id`: Call UUID

**Request Body:**
```json
{
  "outcome": "appointment_booked",
  "notes": "Lead was very interested in our premium membership",
  "summary": "Discussed membership options and scheduled a visit for next Tuesday"
}
```
Note: All fields are optional; only include fields you want to update.

**Response:**
Updated call object

**Usage Example:**
Update call details after completion:
```
PATCH /calls/123e4567-e89b-12d3-a456-426614174000
{
  "outcome": "appointment_booked",
  "notes": "Customer was enthusiastic about joining, scheduled a tour for tomorrow",
  "summary": "Discussed membership tiers, facilities, and scheduled a tour"
}
```

#### 5. Delete Call
```
DELETE /calls/{call_id}
```

**Path Parameter:**
- `call_id`: Call UUID

**Response:**
```json
{
  "message": "Call successfully deleted"
}
```

**Usage Example:**
Delete an erroneous call record:
```
DELETE /calls/123e4567-e89b-12d3-a456-426614174000
```

## Data Models

### Lead Status Values
- `new`
- `contacted`
- `qualified`
- `converted`
- `lost`

### Lead Source Values
- `website`
- `referral`
- `walk_in`
- `phone`
- `social`
- `other`

### Call Direction Values
- `inbound`
- `outbound`

### Call Status Values
- `queued`
- `in_progress`
- `completed`
- `failed`
- `voicemail`
- `missed`

### Call Outcome Values
- `appointment_booked`
- `callback_requested`
- `not_interested`
- `undecided`
- `no_answer`
- `wrong_number`
- `left_message`
- `information_provided`

### Call Sentiment Values
- `positive`
- `neutral`
- `negative` 