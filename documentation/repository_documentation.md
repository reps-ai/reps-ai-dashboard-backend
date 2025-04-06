# Reps AI Dashboard Backend - Repository Documentation

## 1. Introduction

The Reps AI Dashboard Backend is a sophisticated FastAPI application designed to power an AI Voice Agent system specifically tailored for fitness gyms. This backend serves as the central hub for managing gym operations, including lead management, automated call handling, appointment scheduling, and analytics tracking.

The application follows a multi-tenant architecture where multiple gyms can use the platform simultaneously while maintaining data isolation between tenants. Each gym can have multiple branches, staff users, and specific configurations.

## 2. Repository Structure

This repository follows a modern, modular architecture with clear separation of concerns across multiple layers. For detailed documentation on each layer, please refer to the dedicated documentation files:

- [API Layer Documentation](./documentation/api_layer_documentation.md) - Details on API endpoints, request/response schemas, and middleware
- [Service Layer Documentation](./documentation/service_layer_documentation.md) - Information about business logic implementation, service interfaces, and orchestration
- [Database Repository Documentation](./documentation/database_repository_documentation.md) - Details on data models, repository pattern implementation, and query optimization

The repository is organized as follows:

```
reps-ai-dashboard-backend/
├── alembic/              # Database migration tools
├── app/                  # FastAPI application and API routes
│   ├── routes/           # API endpoints organized by domain
│   └── schemas/          # Pydantic models for validation
├── backend/              # Core backend implementation
│   ├── cache/            # Caching mechanisms
│   ├── config/           # Configuration settings
│   ├── db/               # Database interaction
│   │   ├── models/       # SQLAlchemy ORM models
│   │   ├── queries/      # SQL queries
│   │   └── repositories/ # Data access layer
│   ├── integrations/     # External service integrations
│   ├── schemas/          # Shared data schemas
│   ├── services/         # Business logic
│   └── tasks/            # Background task definitions
├── docs/                 # Additional documentation
├── documentation/        # Comprehensive layer documentation
├── scripts/              # Utility scripts
└── tests/                # Test suite
```

## 3. System Overview

### 3.1 Purpose and Functionality

The primary purpose of this backend is to provide gym businesses with an intelligent CRM system enhanced with AI voice capabilities. The system allows gym staff to:

- Track and manage potential customer leads
- Schedule and analyze calls with potential customers
- Book and manage appointments
- Configure and deploy AI voice agents for automated customer interactions
- Maintain a knowledge base to guide AI responses
- Access analytics and performance metrics

### 3.2 Core Technologies

- **FastAPI**: Modern, high-performance web framework
- **PostgreSQL**: Primary database
- **Redis**: Caching and temporary data storage
- **Celery**: Task queue for asynchronous operations
- **Alembic**: Database migration management
- **Pydantic**: Data validation and settings management
- **SQLAlchemy**: ORM for database operations
- **Retell API**: Integration for AI voice agent capabilities

## 4. Architecture

### 4.1 High-Level Architecture

```
┌─────────────────┐     ┌────────────────┐     ┌────────────────┐
│  API Layer      │     │ Service Layer  │     │ Repository     │
│  (FastAPI)      │────▶│ (Business      │────▶│ Layer          │
│                 │     │  Logic)        │     │ (Data Access)  │
└─────────────────┘     └────────────────┘     └────────────────┘
        │                       │                      │
        │                       │                      │
        ▼                       ▼                      ▼
┌─────────────────┐     ┌────────────────┐     ┌────────────────┐
│  Validation     │     │ Background     │     │ Database       │
│  (Pydantic)     │     │ Tasks (Celery) │     │ (PostgreSQL)   │
│                 │     │                │     │                │
└─────────────────┘     └────────────────┘     └────────────────┘
```

The application is built on a layered architecture with clear separation of concerns:

1. **API Layer**: Handles HTTP requests/responses and input validation
2. **Service Layer**: Contains business logic and orchestration
3. **Repository Layer**: Manages data access and persistence
4. **Background Tasks**: Handles asynchronous operations

### 4.2 Multi-tenant Design

The system is designed with multi-tenancy at its core:

- Each gym is a separate tenant with isolated data
- Gyms can have multiple branches
- Users belong to specific gyms and can only access data from their gym
- Role-based permissions control access within a gym

## 5. Key Features

### 5.1 Multi-tenant Isolation

The system ensures complete data isolation between different gym tenants. Key mechanisms include:

- Database filtering based on gym_id
- Request validation to verify resource ownership
- Middleware for tenant context management

See [Database Repository Documentation](./documentation/database_repository_documentation.md) for details on the implementation.

### 5.2 AI Voice Agent Integration

The system integrates with Retell API to provide intelligent voice interactions:

- Dynamic script generation based on lead information
- Context-aware responses using knowledge base
- Call outcome analysis and follow-up scheduling
- Voice customization for brand alignment

See [Service Layer Documentation](./documentation/service_layer_documentation.md) for details on the implementation.

### 5.3 Performance Optimization

Several strategies are employed to ensure high performance:

- Redis caching for frequently accessed data
- Cached HTTP responses for read-heavy endpoints
- Query optimization for database performance
- Background processing for intensive operations

### 5.4 Security Features

The system implements robust security measures:

- JWT-based authentication
- Role-based access control
- Input validation with Pydantic
- Secure password handling
- Rate limiting for API endpoints

## 6. Getting Started

### 6.1 Local Development Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up local environment: `docker-compose up -d` (for PostgreSQL and Redis)
4. Run database migrations: `alembic upgrade head`
5. Start the application: `uvicorn main:app --reload`

The API will be available at http://localhost:8000 with documentation at http://localhost:8000/docs

### 6.2 Environment Variables

Key environment variables:

```
DATABASE_URL=postgresql://user:password@localhost:5432/repsai
REDIS_URL=redis://localhost:6379/0
JWT_SECRET=your-secret-key
RETELL_API_KEY=your-retell-api-key
```

See `backend/config/settings.py` for all available configuration options.

### 6.3 Database Migrations

Database migrations are managed with Alembic:

- Create a new migration: `alembic revision --autogenerate -m "description"`
- Apply migrations: `alembic upgrade head`
- Revert migration: `alembic downgrade -1`

## 7. Development Workflow

### 7.1 Code Organization

- New API endpoints should be added to the appropriate module in `app/routes/`
- Business logic belongs in services in `backend/services/`
- Data access code belongs in repositories in `backend/db/repositories/`
- Background tasks should be defined in `backend/tasks/`

### 7.2 Testing

- Run tests: `pytest`
- Generate coverage report: `pytest --cov=.`

### 7.3 Common Development Tasks

- Adding a new API endpoint: Create route in appropriate module, implement service methods, implement repository methods
- Adding a new model: Create SQLAlchemy model, create Alembic migration, implement repository
- Modifying existing model: Update model, create Alembic migration

## 8. Deployment

### 8.1 Production Deployment

The application can be deployed as a Docker container or directly on a server:

- Docker: Use the provided Dockerfile, set environment variables through Docker configuration
- Direct: Use a process manager like PM2 with the provided pm2.config.js file

### 8.2 Database Management

For production deployments:
- Ensure database backups are configured
- Use connection pooling for optimal performance
- Consider read replicas for high-traffic deployments

### 8.3 Monitoring and Logging

The application includes:
- Structured logging with levels (debug, info, warning, error)
- Health check endpoint at `/health`
- Performance metrics in logs

## 9. Troubleshooting

Common issues and their solutions:

### 9.1 Authentication Issues
- JWT Token Expiration: Check token expiration settings in `backend/config/settings.py`
- Authentication Failures: Verify password hashing in `backend/services/auth/implementation.py`
- Permission Errors: Check role assignments in database and role validation in `app/routes/auth/dependencies.py`

### 9.2 Database Connection Issues
- Connection Pool Exhaustion: Review pool settings in `backend/db/connections/database.py`
- Transaction Deadlocks: Check transaction isolation levels and long-running transactions
- Migration Failures: Inspect Alembic migration files for conflicts or dependencies

### 9.3 Performance Issues
- Slow API Responses: Check for missing indexes, N+1 query problems in repositories
- Cache Ineffectiveness: Review cache invalidation strategies and TTL settings
- Background Task Delays: Monitor Celery worker queue lengths and task execution times

For more specific troubleshooting information, refer to the dedicated layer documentation:
- [API Layer Documentation](./documentation/api_layer_documentation.md)
- [Service Layer Documentation](./documentation/service_layer_documentation.md)
- [Database Repository Documentation](./documentation/database_repository_documentation.md)

## 10. Conclusion

The Reps AI Dashboard Backend is a comprehensive, well-structured application that provides a robust foundation for a gym CRM system with AI voice agent capabilities. Its modular architecture, multi-tenant design, and performance optimizations make it scalable and maintainable for future development.

The system effectively balances performance, security, and feature richness while maintaining clean separation of concerns and following modern best practices for backend development.