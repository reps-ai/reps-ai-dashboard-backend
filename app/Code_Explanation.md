# Reps AI Dashboard Backend - Code Explanation

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Core Components](#core-components)
   - [Authentication](#authentication)
   - [Dependency Injection](#dependency-injection)
   - [Data Models (Schemas)](#data-models-schemas)
   - [API Routes](#api-routes)
4. [Domain Entities](#domain-entities)
   - [Appointments](#appointments)
   - [Calls](#calls)
   - [Leads](#leads)
   - [Knowledge Base](#knowledge-base)
   - [Analytics](#analytics)
   - [Settings](#settings)
5. [Authentication Flow](#authentication-flow)
6. [Data Flow](#data-flow)

## Project Overview

The Reps AI Dashboard Backend is a FastAPI-based application designed to support an AI Voice Agent system for gyms. It provides API endpoints for managing various aspects of gym operations, including lead management, call management, appointment scheduling, and knowledge base management. The system is designed with a multi-tenant architecture where users belong to specific gyms and can only access data from their own gym.

## Architecture

The application follows a modern, modular architecture with the following key components:

- **FastAPI Framework**: Provides the web server and API framework
- **Pydantic Models**: Used for data validation, serialization, and documentation
- **Dependency Injection**: For authentication, authorization, and shared resources
- **JWT Authentication**: For user authentication and session management
- **Modular Routing**: Organized by domain area (calls, appointments, etc.)

The project structure is organized as follows:

```
reps-ai-dashboard-backend/
├── alembic/              # Database migration tools and scripts
├── app/                  # Main application code
│   ├── routes/           # API routes organized by domain
│   ├── schemas/          # Pydantic data models
│   └── dependencies.py   # Shared dependencies and middleware
├── backend/              # Additional backend services
├── docs/                 # Documentation files
├── main.py              # Application entry point
└── requirements.txt     # Python dependencies
```

## Core Components

### Authentication

The application uses OAuth2 with JWT tokens for authentication. The authentication flow is implemented in the auth routes, with token validation handled by the dependency injection system.

Key components:
- **OAuth2PasswordBearer**: For token extraction from requests
- **JWT Encoding/Decoding**: Using the jose library
- **User Model**: Represents authenticated users with roles and permissions

### Dependency Injection

The `dependencies.py` file defines several key dependencies that are injected into route functions:

- **get_current_user**: Extracts and validates the JWT token, returning the authenticated user
- **get_admin_user**: Ensures the current user has admin privileges
- **get_current_gym**: Returns the gym associated with the current user
- **get_current_branch**: Validates and returns a branch within the current gym

These dependencies enforce access control throughout the application, ensuring users can only access data from their own gym.

### Data Models (Schemas)

The application uses Pydantic models for data validation, serialization, and API documentation. These models are organized by domain area in the `app/schemas/` directory.

Common patterns in the schema design:

- **Base Models**: Define the core fields and validation rules
- **Create Models**: Extend base models with fields needed for creation
- **Update Models**: Similar to create models but with optional fields
- **Response Models**: Include additional fields like IDs and timestamps
- **List Response Models**: Include pagination information along with data

Each model uses Pydantic's validation features, including field types, constraints (like min_length), and custom validators.

### API Routes

API routes are organized by domain area in the `app/routes/` directory. Each domain area (appointments, calls, etc.) has its own router with specific endpoints.

Common patterns in the route design:

- **CRUD Operations**: Each entity typically has endpoints for create, read, update, delete
- **Filtering**: List endpoints often support filtering by various criteria
- **Pagination**: List endpoints support pagination with page and limit parameters
- **Dependency Injection**: Routes use dependencies for authentication and access control
- **Response Models**: Each endpoint specifies a Pydantic model for the response

## Domain Entities

### Appointments

Appointments represent scheduled meetings between gym staff and leads/customers.

**Key Models**:
- **AppointmentBase**: Core appointment fields (lead_id, type, date, duration, status, branch_id, notes)
- **AppointmentCreate**: For creating new appointments
- **AppointmentUpdate**: For updating existing appointments
- **AppointmentResponse**: For returning appointment data
- **AppointmentDetailResponse**: Extended response with additional details

**Key Routes**:
- **GET /api/appointments**: List appointments with filtering and pagination
- **GET /api/appointments/{id}**: Get a specific appointment
- **POST /api/appointments**: Create a new appointment
- **PUT /api/appointments/{id}**: Update an existing appointment
- **DELETE /api/appointments/{id}**: Delete an appointment
- **GET /api/appointments/branch/{branch_id}**: List appointments for a specific branch
- **PUT /api/appointments/{id}/status**: Update appointment status

### Calls

Calls represent phone interactions between gym staff and leads/customers.

**Key Models**:
- **CallBase**: Core call fields (lead_id, direction, notes, campaign_id)
- **CallCreate**: For creating new calls, including scheduled calls
- **CallUpdate**: For updating existing calls (outcome, notes, summary)
- **CallResponse**: For returning call data
- **CallDetailResponse**: Extended response with additional details

**Key Routes**:
- **GET /api/calls**: List calls with filtering and pagination
- **GET /api/calls/{id}**: Get a specific call
- **POST /api/calls**: Create a new call record
- **PUT /api/calls/{id}**: Update an existing call
- **POST /api/calls/{id}/notes**: Add notes to a call
- **PUT /api/calls/{id}/outcome**: Update call outcome

### Leads

Leads represent potential customers that the gym is engaged with.

**Key Models**:
- **LeadBase**: Core lead fields (name, email, phone, status, source, etc.)
- **LeadCreate**: For creating new leads
- **LeadUpdate**: For updating existing leads
- **LeadResponse**: For returning lead data
- **LeadDetailResponse**: Extended response with activities and additional details

**Key Routes**:
- **GET /api/leads**: List leads with filtering and pagination
- **GET /api/leads/{id}**: Get a specific lead
- **POST /api/leads**: Create a new lead
- **PUT /api/leads/{id}**: Update an existing lead
- **GET /api/leads/{id}/activities**: Get activities for a lead

### Knowledge Base

The knowledge base stores information that can be used by the AI voice agent to answer questions.

**Key Models**:
- **KnowledgeBase**: Core knowledge fields (question, answer, category, priority)
- **SourceBase**: Information about knowledge sources (name, type, category, url)
- **KnowledgeResponse**: For returning knowledge entries
- **SourceResponse**: For returning source information

**Key Routes**:
- **GET /api/knowledge**: List knowledge entries with filtering and pagination
- **GET /api/knowledge/{id}**: Get a specific knowledge entry
- **POST /api/knowledge**: Create a new knowledge entry
- **PUT /api/knowledge/{id}**: Update an existing knowledge entry
- **DELETE /api/knowledge/{id}**: Delete a knowledge entry
- **GET /api/knowledge/sources**: List knowledge sources
- **POST /api/knowledge/import**: Import knowledge from a source

### Analytics

Analytics provide insights into gym operations and performance.

**Key Routes**:
- **GET /api/analytics/overview**: Get overall performance metrics
- **GET /api/analytics/leads**: Get lead-related analytics
- **GET /api/analytics/calls**: Get call-related analytics
- **GET /api/analytics/appointments**: Get appointment-related analytics

### Settings

Settings allow configuration of various aspects of the system.

**Key Routes**:
- **GET /api/settings/branches**: List branches for the current gym
- **GET /api/settings/users**: List users for the current gym
- **GET /api/settings/campaigns**: List campaigns for the current gym

## Authentication Flow

1. **Login**: User provides credentials to `/api/auth/login`
2. **Token Generation**: System validates credentials and returns a JWT token
3. **Request Authentication**: Subsequent requests include the token in the Authorization header
4. **Token Validation**: The `get_current_user` dependency validates the token on each request
5. **User Context**: The validated user is made available to route handlers

## Data Flow

1. **Request**: Client sends an HTTP request to an API endpoint
2. **Authentication**: The request is authenticated via dependencies
3. **Validation**: Request data is validated using Pydantic models
4. **Processing**: The route handler processes the request
5. **Response**: A response is generated, validated by a Pydantic model, and returned

In a typical flow:

1. User authenticates to get a token
2. User creates a lead via POST /api/leads
3. User schedules a call with the lead via POST /api/calls
4. After the call, the user updates the call outcome and schedules an appointment
5. The appointment is tracked through its lifecycle via status updates

This architecture ensures data integrity, access control, and a clear separation of concerns throughout the application.
