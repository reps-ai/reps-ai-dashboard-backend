# API Layer Documentation

## Table of Contents
1. [Overview](#overview)
2. [Structure](#structure)
3. [Authentication](#authentication)
   - [JWT Authentication](#jwt-authentication)
   - [Auth Endpoints](#auth-endpoints)
4. [API Endpoints](#api-endpoints)
   - [Lead Management API](#lead-management-api)
   - [Call Management API](#call-management-api)
   - [Appointment Management API](#appointment-management-api)
   - [Knowledge Base API](#knowledge-base-api)
   - [Analytics API](#analytics-api)
   - [Voice Agent API](#voice-agent-api)
   - [Settings API](#settings-api)
5. [Data Validation](#data-validation)
   - [Common Schema Components](#common-schema-components)
6. [Middleware](#middleware)
7. [Error Handling](#error-handling)
8. [API Documentation](#api-documentation)
9. [Performance Considerations](#performance-considerations)

## Overview

The API Layer is the entry point for client applications to interact with the Reps AI Dashboard Backend. Built using FastAPI, this layer handles HTTP requests, validates input data, manages authentication, and routes requests to appropriate service components.

## Structure

The API layer is organized in the `app/` directory with the following structure:

```
app/
├── __init__.py
├── dependencies.py            # Dependency injection setup
├── auth/                      # Authentication utilities
│   └── oauth2.py              # JWT token handling
└── routes/                    # API endpoints by domain
    ├── agent/                 # AI agent configuration
    ├── analytics/             # Analytics and reporting
    ├── appointments/          # Appointment management
    ├── auth/                  # Authentication endpoints
    ├── calls/                 # Call management
    ├── knowledge/             # Knowledge base management
    ├── leads/                 # Lead management
    ├── settings/              # System settings
    └── voice_agent/           # Voice agent configuration
```

## Authentication

### JWT Authentication

The system uses JWT (JSON Web Tokens) for authentication with the following components:

- **Token Generation**: Creating signed tokens during login at `app/auth/oauth2.py`
- **Token Validation**: Middleware that validates tokens for protected routes
- **Permission Checking**: Role-based access control implemented in dependencies

### Auth Endpoints

Located at `app/routes/auth/`:

- `POST /auth/login`: Authenticates users and returns a JWT token
- `POST /auth/register`: Creates new user accounts
- `GET /auth/me`: Returns the current authenticated user's profile
- `POST /auth/refresh`: Refreshes an existing JWT token
- `PUT /auth/change-password`: Changes the user's password

Common issues:
- Token expiration settings in `backend/config/settings.py`
- Password hashing inconsistencies in `app/routes/auth/endpoints.py`
- Role permission conflicts in dependency injection

## API Endpoints

### Lead Management API

Located at `app/routes/leads/`:

#### Base Endpoints
- `GET /leads`: List all leads (with filtering, sorting, pagination)
- `POST /leads`: Create a new lead
- `GET /leads/{lead_id}`: Get a specific lead by ID
- `PUT /leads/{lead_id}`: Update a lead
- `DELETE /leads/{lead_id}`: Delete a lead

#### Specialized Endpoints
- `GET /leads/prioritized`: Get leads sorted by priority score
- `GET /leads/search`: Search leads by name, phone, email
- `POST /leads/import`: Bulk import leads from CSV/Excel
- `GET /leads/stats`: Get lead statistics (to be implemented)
- `GET /leads/{lead_id}/calls`: Get all calls associated with a lead (to be implemented)
- `GET /leads/{lead_id}/appointments`: Get all appointments for a lead (to be implemented)

The below "Common issues" sections acts as a proactive approach to troubleshooting and not something that exists in the codebase. 
Common issues:
- Validation errors for required fields in `app/schemas/leads/create.py`
- Filter combination errors in `app/routes/leads/endpoints.py`
- Bulk import handling for large datasets

### Call Management API

Located at `app/routes/calls/`:

#### Base Endpoints
- `GET /calls`: List all calls (with filtering, sorting, pagination)
- `POST /calls`: Log a new call
- `GET /calls/{call_id}`: Get a specific call by ID
- `PUT /calls/{call_id}`: Update call details
- `DELETE /calls/{call_id}`: Delete a call record

#### Specialized Endpoints
- `POST /calls/schedule`: Schedule an automated call
- `GET /calls/metrics`: Get call performance metrics
- `POST /calls/callback`: Webhook for call status updates
- `GET /calls/upcoming`: Get upcoming scheduled calls
- `POST /calls/{call_id}/transcript`: Upload a call transcript

The below "Common issues" sections acts as a proactive approach to troubleshooting and not something that exists in the codebase. 
Common issues:
- Status transition validation in `app/routes/calls/endpoints.py`
- Scheduling conflicts in `app/routes/calls/scheduling.py`
- Webhook signature validation in `app/routes/calls/callbacks.py`

### Appointment Management API

Located at `app/routes/appointments/`:
(All of them are yet to be implemented)
#### Base Endpoints
- `GET /appointments`: List all appointments
- `POST /appointments`: Create a new appointment
- `GET /appointments/{appointment_id}`: Get a specific appointment
- `PUT /appointments/{appointment_id}`: Update an appointment
- `DELETE /appointments/{appointment_id}`: Cancel an appointment

#### Specialized Endpoints
- `GET /appointments/upcoming`: Get upcoming appointments
- `GET /appointments/availability`: Check staff availability
- `POST /appointments/{appointment_id}/remind`: Send appointment reminder
- `PUT /appointments/{appointment_id}/status`: Update appointment status
- `GET /appointments/analytics`: Get appointment conversion metrics

The below "Common issues" sections acts as a proactive approach to troubleshooting and not something that exists in the codebase. 
Common issues:
- Double-booking validation in `app/routes/appointments/endpoints.py`
- Timezone handling in `app/routes/appointments/availability.py`
- Notification delivery in `app/routes/appointments/reminders.py`

### Knowledge Base API

Located at `app/routes/knowledge/`:

(All of them are yet to be implemented)
#### Base Endpoints
- `GET /knowledge`: List all knowledge base entries
- `POST /knowledge`: Create a knowledge base entry
- `GET /knowledge/{entry_id}`: Get a specific knowledge entry
- `PUT /knowledge/{entry_id}`: Update a knowledge entry
- `DELETE /knowledge/{entry_id}`: Delete a knowledge entry

#### Specialized Endpoints
- `GET /knowledge/search`: Search knowledge base
- `POST /knowledge/categories`: Create a new category
- `GET /knowledge/categories`: List all categories


The below "Common issues" sections acts as a proactive approach to troubleshooting and not something that exists in the codebase. 
Common issues:
- Content format validation in `app/routes/knowledge/endpoints.py`
- Search query formatting in `app/routes/knowledge/search.py`
- Large content handling

### Analytics API

Located at `app/routes/analytics/`:

(All of them are yet to be implemented)
#### Dashboard Endpoints
- `GET /analytics/overview`: Get system-wide metrics
- `GET /analytics/leads`: Get lead conversion analytics
- `GET /analytics/calls`: Get call performance metrics
- `GET /analytics/appointments`: Get appointment analytics

#### Reporting Endpoints
- `POST /analytics/reports`: Generate a custom report
- `GET /analytics/reports/{report_id}`: Get a generated report
- `GET /analytics/export`: Export data in various formats


The below "Common issues" sections acts as a proactive approach to troubleshooting and not something that exists in the codebase.
Common issues:
- Calculation errors in metric aggregation
- Performance with large date ranges
- Caching inconsistencies for frequently accessed metrics

### Voice Agent API

Located at `app/routes/voice_agent/`:
(All of them are yet to be implemented)
#### Configuration Endpoints
- `GET /voice-agent/config`: Get voice agent configuration
- `PUT /voice-agent/config`: Update voice agent settings
- `POST /voice-agent/voices`: Create a new voice profile
- `GET /voice-agent/voices`: List all voice profiles

#### Call Management Endpoints
- `POST /voice-agent/calls`: Initiate an AI voice call
- `GET /voice-agent/calls/{call_id}`: Get AI call status
- `PUT /voice-agent/calls/{call_id}/interrupt`: Interrupt an ongoing call
- `POST /voice-agent/script`: Generate or update call script


The below "Common issues" sections acts as a proactive approach to troubleshooting and not something that exists in the codebase.
Common issues:
- Retell API integration in `app/routes/voice_agent/calls.py`
- Voice parameter validation in `app/routes/voice_agent/configuration.py`
- Script generation errors

### Settings API

Located at `app/routes/settings/`:
(All of them are yet to be implemented)

- `GET /settings/gym`: Get gym-specific settings
- `PUT /settings/gym`: Update gym settings
- `GET /settings/user`: Get user preferences
- `PUT /settings/user`: Update user preferences
- `GET /settings/system`: Get system settings (admin only)
- `PUT /settings/system`: Update system settings (admin only)


The below "Common issues" sections acts as a proactive approach to troubleshooting and not something that exists in the codebase.
Common issues:
- Default value conflicts in `app/routes/settings/gym_settings.py`
- Serialization of complex settings objects

## Data Validation

All API input and output is validated using Pydantic models defined in `app/schemas/`:

- **Request Validation**: Ensures incoming data meets requirements
- **Response Serialization**: Formats outgoing data consistently
- **Documentation Generation**: Auto-generates OpenAPI documentation

### Common Schema Components

- **Pagination**: `app/schemas/common/pagination.py` - Handles paginated responses
- **Filtering**: `app/schemas/common/filters.py` - Standardizes query filters
- **Sorting**: `app/schemas/common/sorting.py` - Manages result ordering


The below "Common issues" sections acts as a proactive approach to troubleshooting and not something that exists in the codebase.
Common issues:
- Field validation regex patterns in request schemas
- Missing relationships in response models
- Default value type mismatches

## Middleware

The API layer includes several middleware components:

- **CORS Middleware**: Handles cross-origin requests
- **Authentication Middleware**: Validates JWT tokens
- **HTTP Cache Middleware**: Caches read-heavy endpoints
- **Tenant Context Middleware**: Ensures proper multi-tenant isolation


The below "Common issues" sections acts as a proactive approach to troubleshooting and not something that exists in the codebase.
Common issues:
- Cache key generation in HTTP cache middleware
- CORS configuration for production environments
- Tenant isolation leaks

## Error Handling

The API implements standardized error handling:

- **HTTP Exceptions**: Properly formatted error responses
- **Validation Errors**: Detailed field-level validation feedback
- **Global Exception Handler**: Catches and formats unexpected errors


The below "Common issues" sections acts as a proactive approach to troubleshooting and not something that exists in the codebase.
Common issues:
- Missing error translations
- Inconsistent error formatting
- Overly detailed errors in production

## API Documentation

The API is documented using:

- **OpenAPI/Swagger UI**: Available at `/docs` when running the application
- **ReDoc**: Alternative documentation UI at `/redoc`
- **Markdown Documentation**: Manual documentation in `docs/api_documentation.md`

## Performance Considerations

- **Response Caching**: Frequently accessed endpoints are cached
- **Pagination**: All list endpoints support pagination
- **Async Handlers**: Long-running operations handled asynchronously


The below "Common issues" sections acts as a proactive approach to troubleshooting and not something that exists in the codebase.
Common issues:
- Oversized response payloads
- Missing cache invalidation
- N+1 query problems in nested responses