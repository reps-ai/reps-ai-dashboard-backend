# Backend Processing System

This directory contains the backend processing system for the AI Dashboard. It handles campaign management, call processing, lead management, and analytics.

## Directory Structure

### `/services`
Contains the core business logic services:
- `/campaign` - Campaign management service
- `/lead` - Lead management service
- `/call` - Call processing service
- `/analytics` - Analytics and reporting service

### `/integrations`
Contains integrations with external services:
- `/retell` - Integration with Retell for call handling
- `/ai_services` - Integration with AI services for transcript analysis, sentiment analysis, etc.

### `/tasks`
Contains background task definitions:
- `/campaign` - Campaign scheduling tasks
- `/call` - Call processing tasks
- `/analytics` - Analytics generation tasks

### `/db`
Contains database-related code:
- `/models` - Database models (placeholder, will be implemented separately)
- `/repositories` - Data access layer for interacting with the database

### `/utils`
Contains utility functions and helpers:
- `/logging` - Logging utilities
- `/helpers` - General helper functions
- `/constants` - Constant definitions

### `/config`
Contains configuration files and settings management

### `/tests`
Contains test files for the backend system

## Integration with FastAPI App

This backend system integrates with the existing FastAPI app in the `/app` directory. The FastAPI app serves as the API layer for the dashboard, while this backend system handles the processing logic.

## Development Guidelines

1. Each service should be self-contained with clear interfaces
2. Use dependency injection for service dependencies
3. Background tasks should be idempotent when possible
4. All external integrations should have proper error handling and retry logic
5. Follow the repository pattern for database access 