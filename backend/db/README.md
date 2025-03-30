# Database Layer

## Overview

This directory contains the database layer implementation for the AI Dashboard backend. It uses SQLAlchemy as the ORM with async support and is designed to work with PostgreSQL (specifically optimized for Neon).

## Directory Structure

```
db/
├── connections/     # Database connection management
├── exceptions/      # Custom database exceptions
├── helpers/         # Database helper functions
├── migrations/      # Database migration scripts
├── models/         # SQLAlchemy models
├── queries/        # Raw SQL queries
├── repositories/   # Data access layer
├── scripts/        # Database maintenance scripts
├── transactions/   # Transaction management
└── types/         # Custom database types
```

## Setup and Configuration

### Environment Variables

The database connection is configured using environment variables:

```
DATABASE_URL=postgresql+asyncpg://user:password@host:port/database
```

### Connection Management

- Uses SQLAlchemy's async engine with connection pooling
- Special handling for Neon database SSL configuration
- Implements async context manager pattern for session management

Example usage:

```python
from db.connections.database import get_db

async with get_db() as db:
    # Perform database operations
    await db.execute(...)
    await db.commit()
```

## Key Components

### Models

- Built on SQLAlchemy declarative base
- Organized by domain (analytics, call, campaign, etc.)
- Common models include:
  - User
  - Member
  - Appointment
  - AISettings
  - VoiceSettings

### Repositories

Each domain has its own repository class implementing:

- CRUD operations
- Domain-specific queries
- Transaction management
- Error handling

### Migrations

- Managed through Alembic
- Version controlled schema changes
- Both upgrade and downgrade paths
- Migration scripts in `migrations/versions/`

## Best Practices

### Connection Management

1. Always use the `get_db()` context manager for database sessions
2. Close connections properly using the context manager
3. Configure appropriate pool sizes for your use case

### Query Performance

1. Use SQLAlchemy's relationship loading strategies appropriately
2. Implement indexes for frequently queried fields
3. Use async queries for better performance
4. Implement pagination for large result sets

### Error Handling

1. Use custom exceptions for specific database errors
2. Implement proper error reporting
3. Handle connection errors gracefully
4. Log database operations appropriately

## Security

### Connection Security

- SSL enabled for database connections
- Special handling for Neon database security requirements
- Environment-based configuration

### Data Access

- Repository pattern for controlled data access
- Input validation through SQLAlchemy models
- Parameterized queries to prevent SQL injection

## Testing

The database layer includes:

- Unit tests for models and repositories
- Integration tests for database operations
- Test utilities and fixtures
- Mock database for testing

For running tests:

```bash
pytest tests/db_repo/
```

## Maintenance

### Common Tasks

1. Creating new migrations:

```bash
alembic revision -m "description_of_change"
```

2. Applying migrations:

```bash
alembic upgrade head
```

3. Rolling back migrations:

```bash
alembic downgrade -1
```

### Performance Monitoring

- Monitor connection pool usage
- Watch for slow queries
- Regular index maintenance
- Connection pool health checks

## Dependencies

- SQLAlchemy: ORM and database toolkit
- asyncpg: Async PostgreSQL driver
- alembic: Database migration tool
- pydantic: Settings management and validation

## Contributing

When adding new features to the database layer:

1. Follow the existing directory structure
2. Create appropriate migrations
3. Update relevant repositories
4. Add tests for new functionality
5. Document changes in relevant README files
