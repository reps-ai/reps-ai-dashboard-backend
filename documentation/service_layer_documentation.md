# Service Layer Documentation

## Overview

The Service Layer is the heart of the Reps AI Dashboard Backend, implementing the core business logic that powers the application. It sits between the API layer and the repository layer, orchestrating complex operations, enforcing business rules, and coordinating between different components of the system.

## Architecture

The service layer follows a clean architecture approach with:
- **Interface-based design**: Services are defined by interfaces and implemented separately
- **Dependency injection**: Dependencies are provided through constructors
- **Factory pattern**: Service instances are created through factory classes

```
backend/services/
├── __init__.py
├── analytics/            # Analytics processing services
├── appointment/          # Appointment management services
├── auth/                 # Authentication services
├── call/                 # Call management services
├── campaign/             # Campaign management services
├── knowledge/            # Knowledge base services
├── lead/                 # Lead management services
├── notification/         # Notification services
└── voice_agent/          # AI voice agent services
```

## Core Service Components

### Lead Service

Located at `backend/services/lead/`:

- `interface.py`: Defines the LeadService interface
- `implementation.py`: Implements lead management functionality
- `factory.py`: Creates and configures LeadService instances
- `prioritization.py`: Implements lead scoring and prioritization algorithms

**Key Responsibilities:**
- Managing lead lifecycle (creation, update, deletion)
- Lead scoring and qualification
- Lead tagging and categorization
- Lead search and filtering
- Bulk import processing

**Common Issues:**
- Complex lead qualification logic errors in `implementation.py`
- Scoring algorithm issues in `prioritization.py`
- Performance bottlenecks with large lead datasets
- Concurrency issues with simultaneous lead updates

### Call Service

Located at `backend/services/call/`:

- `interface.py`: Defines the CallService interface
- `implementation.py`: Implements call management functionality
- `factory.py`: Creates and configures CallService instances
- `retell_integration.py`: Handles Retell API communication
- `scheduling.py`: Implements call scheduling algorithms

**Key Responsibilities:**
- Call logging and management
- Call scheduling and execution
- Call outcome tracking
- Integration with Retell voice API
- Call analytics and performance metrics

**Common Issues:**
- Scheduling algorithm errors in `implementation.py`
- Status transition logic failures
- API integration issues in `retell_integration.py`
- Race conditions in call status updates

### Appointment Service

Located at `backend/services/appointment/`:

- `interface.py`: Defines the AppointmentService interface
- `implementation.py`: Implements appointment management functionality
- `factory.py`: Creates and configures AppointmentService instances
- `reminder.py`: Handles appointment reminder logic

**Key Responsibilities:**
- Appointment scheduling and management
- Availability checking and conflict resolution
- Appointment status tracking
- Reminder scheduling and delivery
- Conversion tracking

**Common Issues:**
- Availability calculation errors in `implementation.py`
- Conflict resolution failures for overlapping appointments
- Timezone handling issues
- Reminder delivery failures in `reminder.py`

### Analytics Service

Located at `backend/services/analytics/`:

- `interface.py`: Defines the AnalyticsService interface
- `implementation.py`: Implements analytics calculation functionality
- `factory.py`: Creates and configures AnalyticsService instances
- `reports.py`: Handles report generation

**Key Responsibilities:**
- Metric calculation and aggregation
- Trend analysis and forecasting
- Report generation
- Data export
- Performance benchmarking

**Common Issues:**
- Calculation errors in complex metrics in `implementation.py`
- Performance issues with large datasets
- Caching inconsistencies
- Memory usage issues in report generation in `reports.py`

### Voice Agent Service

Located at `backend/services/voice_agent/`:

- `interface.py`: Defines the VoiceAgentService interface
- `implementation.py`: Implements voice agent functionality
- `factory.py`: Creates and configures VoiceAgentService instances
- `script_generation.py`: Dynamic script generation for voice calls

**Key Responsibilities:**
- Voice agent configuration
- Call script generation
- Voice call execution and monitoring
- Call interruption and control
- Call transcription and analysis

**Common Issues:**
- Context processing errors in `script_generation.py`
- Template rendering issues
- Retell API integration problems in `implementation.py`
- Voice parameter validation failures

### Knowledge Base Service

Located at `backend/services/knowledge/`:

- `interface.py`: Defines the KnowledgeService interface
- `implementation.py`: Implements knowledge base functionality
- `factory.py`: Creates and configures KnowledgeService instances
- `search.py`: Implements knowledge base search

**Key Responsibilities:**
- Knowledge content management
- Content categorization
- Search functionality
- Content validation
- Integration with AI voice agents

**Common Issues:**
- Search algorithm issues in `search.py`
- Content format validation problems
- Large content handling
- Category hierarchy management

## Service Patterns

### Interface Design

All services follow a consistent interface pattern:

```python
class IExampleService(Protocol):
    def create_example(self, data: ExampleCreate, user_id: UUID) -> Example:
        ...
    
    def get_example(self, example_id: UUID, user_id: UUID) -> Optional[Example]:
        ...
    
    def update_example(self, example_id: UUID, data: ExampleUpdate, user_id: UUID) -> Optional[Example]:
        ...
    
    def delete_example(self, example_id: UUID, user_id: UUID) -> bool:
        ...
```

This ensures consistent API across implementations and facilitates testing and mocking.

### Factory Pattern

Services are instantiated through factories to manage dependencies:

```python
class ExampleServiceFactory:
    @staticmethod
    def create(db_session: Session) -> IExampleService:
        # Create repository dependencies
        example_repository = ExampleRepository(db_session)
        
        # Create service with dependencies
        return ExampleService(example_repository)
```

This centralizes dependency creation and configuration.

### Implementation Structure

Service implementations follow a standard pattern:

```python
class ExampleService(IExampleService):
    def __init__(self, example_repository: IExampleRepository):
        self.example_repository = example_repository
    
    def create_example(self, data: ExampleCreate, user_id: UUID) -> Example:
        # Validate business rules
        self._validate_example(data)
        
        # Process data as needed
        processed_data = self._process_example_data(data)
        
        # Use repository to persist
        return self.example_repository.create(processed_data, user_id)
    
    # Private helper methods
    def _validate_example(self, data: ExampleCreate) -> None:
        # Implementation of business rule validation
        pass
    
    def _process_example_data(self, data: ExampleCreate) -> Dict[str, Any]:
        # Implementation of data transformation
        pass
```

This separates public API from internal implementation details.

## Caching Strategies

The service layer implements several caching strategies:

### Method-Level Caching

Frequently accessed methods use decorators for caching:

```python
@service_cache(ttl=300)
def get_prioritized_leads(self, gym_id: UUID, limit: int = 20) -> List[Lead]:
    # Implementation
```

Common issues:
- Cache key collisions
- Stale data due to missed invalidation
- Over-caching of volatile data

### Result Aggregation Caching

Complex calculations are cached to improve performance:

```python
@service_cache(ttl=3600)
def calculate_lead_conversion_metrics(self, gym_id: UUID, start_date: date, end_date: date) -> Dict[str, Any]:
    # Complex calculation
```

Common issues:
- Memory usage for large result sets
- Inappropriate TTL for data volatility
- Cache invalidation timing

## Transactions

The service layer manages database transactions for operations that require atomicity:

```python
def create_appointment_with_notification(self, data: AppointmentCreate, user_id: UUID) -> Appointment:
    try:
        # Start transaction
        self.transaction_manager.begin()
        
        # Create appointment
        appointment = self.appointment_repository.create(data, user_id)
        
        # Schedule notification
        self.notification_service.schedule_appointment_notification(appointment.id)
        
        # Commit transaction
        self.transaction_manager.commit()
        return appointment
    except Exception as e:
        # Rollback on error
        self.transaction_manager.rollback()
        raise e
```

Common issues:
- Transaction leakage
- Deadlocks in concurrent operations
- Inappropriate transaction boundaries

## Error Handling

The service layer implements domain-specific error handling:

```python
def update_call_status(self, call_id: UUID, new_status: str, user_id: UUID) -> Call:
    try:
        # Get the call
        call = self.call_repository.get_by_id(call_id)
        if not call:
            raise EntityNotFoundError(f"Call with ID {call_id} not found")
        
        # Validate status transition
        if not self._is_valid_status_transition(call.status, new_status):
            raise InvalidStatusTransitionError(
                f"Cannot transition from {call.status} to {new_status}"
            )
        
        # Update and return
        return self.call_repository.update_status(call_id, new_status, user_id)
    except (EntityNotFoundError, InvalidStatusTransitionError) as e:
        # Log and re-raise domain exceptions
        self.logger.warning(f"Domain error in update_call_status: {str(e)}")
        raise
    except Exception as e:
        # Log and convert to generic service error
        self.logger.error(f"Unexpected error in update_call_status: {str(e)}")
        raise ServiceError(f"Failed to update call status: {str(e)}")
```

Common issues:
- Inconsistent error handling across services
- Missing error translation for client-friendly messages
- Inappropriate error classification

## Service Integration

Services integrate with each other through direct dependencies:

```python
class AppointmentService(IAppointmentService):
    def __init__(
        self,
        appointment_repository: IAppointmentRepository,
        lead_service: ILeadService,
        notification_service: INotificationService
    ):
        self.appointment_repository = appointment_repository
        self.lead_service = lead_service
        self.notification_service = notification_service
    
    def create_appointment(self, data: AppointmentCreate, user_id: UUID) -> Appointment:
        # Validate lead exists
        lead = self.lead_service.get_lead(data.lead_id, user_id)
        if not lead:
            raise EntityNotFoundError(f"Lead with ID {data.lead_id} not found")
        
        # Create appointment
        appointment = self.appointment_repository.create(data, user_id)
        
        # Schedule notification
        self.notification_service.schedule_appointment_notification(appointment.id)
        
        return appointment
```

Common issues:
- Circular dependencies
- Tight coupling between services
- Cross-service transaction management

## Background Task Integration

Services delegate long-running operations to background tasks:

```python
def generate_analytics_report(self, report_config: ReportConfig, user_id: UUID) -> UUID:
    # Create a pending report record
    report_id = self.report_repository.create_pending(report_config, user_id)
    
    # Queue background task
    self.task_queue.enqueue(
        "analytics.tasks.generate_report",
        report_id=report_id,
        config=report_config.dict(),
        user_id=user_id
    )
    
    return report_id
```

Common issues:
- Task queue configuration errors
- Result handling and status updates
- Error recovery for failed tasks

## Performance Considerations

The service layer implements several performance optimizations:

- **Batch Processing**: Handling multiple entities at once
- **Lazy Loading**: Deferring expensive operations until needed
- **Caching**: Storing frequently accessed results
- **Pagination**: Processing large datasets in chunks
- **Asynchronous Operations**: Non-blocking execution for I/O bound operations

Common issues:
- Memory usage with large datasets
- N+1 query patterns
- Cache invalidation timing
- Concurrent operation conflicts

## Testing Approach

Services are designed for testability:

- **Interface-based mocking**: Dependencies can be easily mocked
- **Pure business logic**: Core algorithms are separated from I/O
- **Factory configuration**: Test implementations can be injected

Common testing patterns:
- Unit tests with mocked dependencies
- Integration tests with test repositories
- Behavioral tests with service combinations
- Performance tests for critical operations