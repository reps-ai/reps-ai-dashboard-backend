# Database Repository Layer Documentation

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Database Models](#database-models)
   - [Core Model Structure](#core-model-structure)
   - [Multi-tenant Design](#multi-tenant-design)
   - [Key Database Models](#key-database-models)
     - [User and Authentication Models](#user-and-authentication-models)
     - [Gym and Branch Models](#gym-and-branch-models)
     - [Lead Models](#lead-models)
     - [Call Models](#call-models)
     - [Appointment Models](#appointment-models)
4. [Repository Pattern Implementation](#repository-pattern-implementation)
   - [Base Repository](#base-repository)
   - [Specialized Repositories](#specialized-repositories)
     - [Lead Repository](#lead-repository)
     - [Call Repository](#call-repository)
     - [Appointment Repository](#appointment-repository)
5. [Query Patterns](#query-patterns)
   - [Tenant Isolation](#tenant-isolation)
   - [Eager Loading](#eager-loading)
   - [Pagination, Filtering, and Sorting](#pagination-filtering-and-sorting)
6. [Caching Integration](#caching-integration)
7. [Transaction Management](#transaction-management)
8. [Raw SQL Queries](#raw-sql-queries)
9. [Performance Optimization](#performance-optimization)
   - [Indexing](#indexing)
   - [Query Optimization](#query-optimization)
   - [Result Caching](#result-caching)
10. [Repository Lifecycle Management](#repository-lifecycle-management)
    - [Connection Pooling](#connection-pooling)
    - [Session Management](#session-management)
    - [Repository Initialization](#repository-initialization)
11. [Repository Factory Pattern](#repository-factory-pattern)
    - [Repository Registration](#repository-registration)
12. [Cache Invalidation Strategies](#cache-invalidation-strategies)
    - [Key-based Invalidation](#key-based-invalidation)
    - [Pattern-based Invalidation](#pattern-based-invalidation)
    - [Dependent Cache Invalidation](#dependent-cache-invalidation)
13. [Data Migration and Versioning](#data-migration-and-versioning)
    - [Alembic Integration](#alembic-integration)
    - [Model Versioning Strategies](#model-versioning-strategies)
    - [Migration Best Practices](#migration-best-practices)
14. [Monitoring and Instrumentation](#monitoring-and-instrumentation)
    - [Query Timing](#query-timing)
    - [Cache Effectiveness](#cache-effectiveness)
    - [Health Checks](#health-checks)
15. [Testing Approach](#testing-approach)
16. [Common Repository Issues](#common-repository-issues)
    - [N+1 Query Problem](#1-n1-query-problem)
    - [Transaction Management Issues](#2-transaction-management-issues)
    - [Missing Tenant Isolation](#3-missing-tenant-isolation)
    - [Inefficient Query Patterns](#4-inefficient-query-patterns)
17. [Conclusion](#conclusion)

## Overview

The Database Repository Layer in the Reps AI Dashboard Backend provides a clean abstraction for data access and persistence. This layer serves as the interface between the business logic in the Service Layer and the database, implementing data access patterns, query optimization, and ensuring data integrity.

## Architecture

The repository layer follows the Repository Pattern with:
- **Interface-based design**: Repositories are defined by interfaces
- **Implementation separation**: Database-specific implementations are isolated
- **Query encapsulation**: Complex queries are encapsulated within repositories
- **Multi-tenant isolation**: Data access is scoped to tenant (gym) context

```
backend/db/
├── __init__.py
├── base.py                # SQLAlchemy base configuration
├── config.py              # Database connection configuration
├── connections/           # Database connection management
│   └── database.py        # Session and connection pool management
├── models/                # SQLAlchemy ORM models
│   ├── base.py            # Base model with common fields
│   ├── user.py            # User and authentication models
│   ├── appointment.py     # Appointment models
│   ├── ai_settings.py     # AI configuration models
│   ├── voice_settings.py  # Voice settings models
│   ├── analytics/         # Analytics models
│   ├── call/              # Call and campaign models
│   ├── gym/               # Gym and branch models
│   ├── lead/              # Lead management models
│   └── common/            # Shared model components
├── queries/               # Raw SQL queries
└── repositories/          # Data access repositories
    ├── base.py            # Generic repository implementation
    ├── appointment/       # Appointment repositories
    ├── analytics/         # Analytics repositories
    ├── call/              # Call repositories
    ├── gym/               # Gym repositories
    ├── knowledge/         # Knowledge base repositories
    ├── lead/              # Lead repositories
    └── user/              # User repositories
```

## Database Models

### Core Model Structure

All models inherit from a common base defined in `backend/db/models/base.py`:

```python
class Base(DeclarativeBase):
    """Base class for all models"""
    pass

class TimestampMixin:
    """Adds created_at and updated_at fields to models"""
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class BaseModel(Base, TimestampMixin):
    """Base model with ID and timestamps"""
    __abstract__ = True
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
```

Common issues:
- Inheritance issues with mixins
- Column type conflicts between parent and child classes
- Abstract base class configuration errors

### Multi-tenant Design

Models implement multi-tenancy through foreign keys to the Gym model:

```python
class Lead(BaseModel):
    """Lead model for potential gym customers"""
    __tablename__ = "lead"
    
    # Tenant isolation
    gym_id = Column(UUID(as_uuid=True), ForeignKey("gym.id", ondelete="CASCADE"), nullable=False, index=True)
    gym = relationship("Gym", back_populates="leads")
    
    # Lead fields
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=False)
    # ... other fields ...
    
    # Relationships
    calls = relationship("CallLog", back_populates="lead", cascade="all, delete-orphan")
    appointments = relationship("Appointment", back_populates="lead", cascade="all, delete-orphan")
    tags = relationship("LeadTag", secondary="lead_tag_association", back_populates="leads")
    qualification = relationship("LeadQualification", back_populates="lead", uselist=False, cascade="all, delete-orphan")
```

Common issues:
- Missing foreign key constraints
- Incorrect cascade behavior
- Index configuration for tenant filtering
- Relationship configuration errors

### Key Database Models

#### User and Authentication Models

**User Model (`backend/db/models/user.py`)**:
```python
class User(BaseModel):
    __tablename__ = "user"
    
    # User identity
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # User information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    
    # Tenant association
    gym_id = Column(UUID(as_uuid=True), ForeignKey("gym.id", ondelete="CASCADE"), nullable=False)
    gym = relationship("Gym", back_populates="users")
    
    # Role association
    role_id = Column(Integer, ForeignKey("role.id"), nullable=False)
    role = relationship("Role", back_populates="users")
    
    # Optional profile information
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
```

Common issues:
- Password hash generation and comparison
- Email uniqueness enforcement
- Role permission association

#### Gym and Branch Models

**Gym Model (`backend/db/models/gym/gym.py`)**:
```python
class Gym(BaseModel):
    __tablename__ = "gym"
    
    # Basic information
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Contact information
    email = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    website = Column(String(255), nullable=True)
    
    # Relationships
    branches = relationship("Branch", back_populates="gym", cascade="all, delete-orphan")
    users = relationship("User", back_populates="gym", cascade="all, delete-orphan")
    leads = relationship("Lead", back_populates="gym", cascade="all, delete-orphan")
    settings = relationship("GymSettings", back_populates="gym", uselist=False, cascade="all, delete-orphan")
    knowledge_base = relationship("KnowledgeBaseEntry", back_populates="gym", cascade="all, delete-orphan")
```

**Branch Model (`backend/db/models/gym/branch.py`)**:
```python
class Branch(BaseModel):
    __tablename__ = "branch"
    
    # Tenant association
    gym_id = Column(UUID(as_uuid=True), ForeignKey("gym.id", ondelete="CASCADE"), nullable=False)
    gym = relationship("Gym", back_populates="branches")
    
    # Branch information
    name = Column(String(255), nullable=False)
    address = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    zip_code = Column(String(20), nullable=True)
    phone = Column(String(20), nullable=True)
    
    # Relationships
    leads = relationship("Lead", back_populates="branch")
    appointments = relationship("Appointment", back_populates="branch")
```

Common issues:
- Cascading delete configuration
- Foreign key constraints
- One-to-one relationship configuration

#### Lead Models

**Lead Model (`backend/db/models/lead/lead.py`)**:
```python
class Lead(BaseModel):
    __tablename__ = "lead"
    
    # Tenant isolation
    gym_id = Column(UUID(as_uuid=True), ForeignKey("gym.id", ondelete="CASCADE"), nullable=False, index=True)
    gym = relationship("Gym", back_populates="leads")
    
    # Branch association (optional)
    branch_id = Column(UUID(as_uuid=True), ForeignKey("branch.id", ondelete="SET NULL"), nullable=True)
    branch = relationship("Branch", back_populates="leads")
    
    # Lead information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=False, index=True)
    
    # Lead status
    status = Column(Enum("new", "contacted", "qualified", "converted", "lost", name="lead_status"), default="new", nullable=False)
    source = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    calls = relationship("CallLog", back_populates="lead", cascade="all, delete-orphan")
    appointments = relationship("Appointment", back_populates="lead", cascade="all, delete-orphan")
    tags = relationship("LeadTag", secondary="lead_tag_association", back_populates="leads")
    qualification = relationship("LeadQualification", back_populates="lead", uselist=False, cascade="all, delete-orphan")
```

Common issues:
- Phone number uniqueness
- Index configuration for frequent queries
- Many-to-many relationship with tags

#### Call Models

**Call Log Model (`backend/db/models/call/call_log.py`)**:
```python
class CallLog(BaseModel):
    __tablename__ = "call_log"
    
    # Tenant isolation
    gym_id = Column(UUID(as_uuid=True), ForeignKey("gym.id", ondelete="CASCADE"), nullable=False, index=True)
    gym = relationship("Gym")
    
    # Call associations
    lead_id = Column(UUID(as_uuid=True), ForeignKey("lead.id", ondelete="CASCADE"), nullable=False, index=True)
    lead = relationship("Lead", back_populates="calls")
    
    # Call information
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    duration = Column(Integer, nullable=True)  # in seconds
    
    # Call outcomes
    status = Column(Enum("scheduled", "in_progress", "completed", "failed", "no_answer", name="call_status"), default="scheduled", nullable=False)
    outcome = Column(Enum("appointment_booked", "follow_up_needed", "not_interested", "wrong_number", "voicemail", "no_answer", "other", name="call_outcome"), nullable=True)
    notes = Column(Text, nullable=True)
    
    # AI voice agent details
    is_ai_call = Column(Boolean, default=False, nullable=False)
    retell_call_id = Column(String(255), nullable=True)
    
    # Relationships
    transcript = relationship("CallTranscript", back_populates="call", uselist=False, cascade="all, delete-orphan")
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaign.id", ondelete="SET NULL"), nullable=True)
    campaign = relationship("Campaign")
```

Common issues:
- Status enum validation
- Duration calculation
- Foreign key constraints with leads

#### Appointment Models

**Appointment Model (`backend/db/models/appointment.py`)**:
```python
class Appointment(BaseModel):
    __tablename__ = "appointment"
    
    # Tenant isolation
    gym_id = Column(UUID(as_uuid=True), ForeignKey("gym.id", ondelete="CASCADE"), nullable=False, index=True)
    gym = relationship("Gym")
    
    # Appointment associations
    lead_id = Column(UUID(as_uuid=True), ForeignKey("lead.id", ondelete="CASCADE"), nullable=False, index=True)
    lead = relationship("Lead", back_populates="appointments")
    
    branch_id = Column(UUID(as_uuid=True), ForeignKey("branch.id", ondelete="SET NULL"), nullable=True)
    branch = relationship("Branch", back_populates="appointments")
    
    # Staff assignment
    staff_id = Column(UUID(as_uuid=True), ForeignKey("user.id", ondelete="SET NULL"), nullable=True)
    staff = relationship("User")
    
    # Appointment details
    scheduled_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Status
    status = Column(Enum("scheduled", "confirmed", "completed", "cancelled", "no_show", name="appointment_status"), default="scheduled", nullable=False)
    
    # Tracking
    call_id = Column(UUID(as_uuid=True), ForeignKey("call_log.id", ondelete="SET NULL"), nullable=True)
    call = relationship("CallLog")
```

Common issues:
- Datetime handling
- Scheduling conflicts
- Status transitions

## Repository Pattern Implementation

### Base Repository

The foundation for all repositories is defined in `backend/db/repositories/base.py`:

```python
class BaseRepository(Generic[T]):
    """
    Generic repository providing common data access methods.
    """
    
    def __init__(self, db_session: Session, model_class: Type[T]):
        self.db = db_session
        self.model_class = model_class
    
    def get_by_id(self, entity_id: UUID, tenant_id: Optional[UUID] = None) -> Optional[T]:
        """Get an entity by ID with optional tenant filtering."""
        query = self.db.query(self.model_class).filter(self.model_class.id == entity_id)
        
        if tenant_id is not None and hasattr(self.model_class, 'gym_id'):
            query = query.filter(self.model_class.gym_id == tenant_id)
            
        return query.first()
    
    def list(self, 
             tenant_id: Optional[UUID] = None, 
             skip: int = 0, 
             limit: int = 100,
             filters: Optional[Dict[str, Any]] = None,
             sort_by: Optional[str] = None,
             sort_dir: Optional[str] = None) -> List[T]:
        """
        List entities with pagination, filtering, and sorting.
        Automatically applies tenant isolation if applicable.
        """
        query = self.db.query(self.model_class)
        
        # Apply tenant isolation
        if tenant_id is not None and hasattr(self.model_class, 'gym_id'):
            query = query.filter(self.model_class.gym_id == tenant_id)
        
        # Apply custom filters
        if filters:
            query = self._apply_filters(query, filters)
        
        # Apply sorting
        if sort_by:
            query = self._apply_sorting(query, sort_by, sort_dir)
        
        # Apply pagination
        return query.offset(skip).limit(limit).all()
    
    def create(self, data: Dict[str, Any], tenant_id: Optional[UUID] = None) -> T:
        """Create a new entity, automatically setting tenant ID if applicable."""
        # Create entity from data
        entity_data = data.copy()
        
        # Set tenant ID if applicable
        if tenant_id is not None and hasattr(self.model_class, 'gym_id'):
            entity_data['gym_id'] = tenant_id
        
        # Create and save entity
        entity = self.model_class(**entity_data)
        self.db.add(entity)
        self.db.flush()
        
        return entity
    
    def update(self, entity_id: UUID, data: Dict[str, Any], tenant_id: Optional[UUID] = None) -> Optional[T]:
        """Update an existing entity with tenant validation."""
        # Get entity
        entity = self.get_by_id(entity_id, tenant_id)
        if not entity:
            return None
        
        # Update fields
        for key, value in data.items():
            if hasattr(entity, key):
                setattr(entity, key, value)
        
        self.db.flush()
        return entity
    
    def delete(self, entity_id: UUID, tenant_id: Optional[UUID] = None) -> bool:
        """Delete an entity with tenant validation."""
        entity = self.get_by_id(entity_id, tenant_id)
        if not entity:
            return False
        
        self.db.delete(entity)
        self.db.flush()
        return True
    
    # Helper methods for query building
    def _apply_filters(self, query: Query, filters: Dict[str, Any]) -> Query:
        """Apply filters to query."""
        for key, value in filters.items():
            if hasattr(self.model_class, key):
                if isinstance(value, list):
                    query = query.filter(getattr(self.model_class, key).in_(value))
                else:
                    query = query.filter(getattr(self.model_class, key) == value)
        return query
    
    def _apply_sorting(self, query: Query, sort_by: str, sort_dir: Optional[str] = None) -> Query:
        """Apply sorting to query."""
        if hasattr(self.model_class, sort_by):
            column = getattr(self.model_class, sort_by)
            if sort_dir and sort_dir.lower() == 'desc':
                return query.order_by(desc(column))
            return query.order_by(column)
        return query
```

Common issues:
- Generic type handling
- Filter application errors
- Dynamic attribute access

### Specialized Repositories

#### Lead Repository

Located at `backend/db/repositories/lead/lead_repository.py`:

```python
class LeadRepository(BaseRepository[Lead]):
    """
    Repository for Lead entity with specialized query methods.
    """
    
    def __init__(self, db_session: Session):
        super().__init__(db_session, Lead)
    
    def find_by_phone(self, phone: str, tenant_id: UUID) -> Optional[Lead]:
        """Find a lead by phone number within a specific tenant."""
        return self.db.query(Lead).filter(
            Lead.phone == phone,
            Lead.gym_id == tenant_id
        ).first()
    
    def get_prioritized_leads(self, tenant_id: UUID, limit: int = 20) -> List[Lead]:
        """
        Get leads ordered by priority score for a specific tenant.
        Joins with qualification data for scoring.
        """
        return self.db.query(Lead).join(
            LeadQualification, 
            Lead.id == LeadQualification.lead_id
        ).filter(
            Lead.gym_id == tenant_id,
            Lead.status.in_(["new", "contacted", "qualified"])
        ).order_by(
            desc(LeadQualification.score),
            Lead.created_at.desc()
        ).limit(limit).all()
    
    def search(self, query: str, tenant_id: UUID, limit: int = 20) -> List[Lead]:
        """
        Search leads by name, email, or phone.
        """
        search_term = f"%{query}%"
        return self.db.query(Lead).filter(
            Lead.gym_id == tenant_id,
            or_(
                Lead.first_name.ilike(search_term),
                Lead.last_name.ilike(search_term),
                Lead.email.ilike(search_term),
                Lead.phone.ilike(search_term)
            )
        ).limit(limit).all()
    
    def get_with_relationships(self, lead_id: UUID, tenant_id: UUID) -> Optional[Lead]:
        """
        Get a lead with eager-loaded relationships.
        """
        return self.db.query(Lead).options(
            joinedload(Lead.qualification),
            joinedload(Lead.tags),
            joinedload(Lead.calls),
            joinedload(Lead.appointments)
        ).filter(
            Lead.id == lead_id,
            Lead.gym_id == tenant_id
        ).first()
    
    def get_lead_conversion_stats(self, tenant_id: UUID, start_date: date, end_date: date) -> Dict[str, int]:
        """
        Get lead conversion statistics for a date range.
        """
        results = self.db.query(
            Lead.status,
            func.count(Lead.id).label('count')
        ).filter(
            Lead.gym_id == tenant_id,
            Lead.created_at >= start_date,
            Lead.created_at <= end_date
        ).group_by(
            Lead.status
        ).all()
        
        # Convert to dictionary
        stats = {status: 0 for status in ["new", "contacted", "qualified", "converted", "lost"]}
        for status, count in results:
            stats[status] = count
            
        return stats
```

Common issues:
- Join query optimization
- Query result mapping
- Complex filtering logic

#### Call Repository

Located at `backend/db/repositories/call/call_repository.py`:

```python
class CallRepository(BaseRepository[CallLog]):
    """
    Repository for CallLog entity with specialized query methods.
    """
    
    def __init__(self, db_session: Session):
        super().__init__(db_session, CallLog)
    
    def get_upcoming_calls(self, tenant_id: UUID, limit: int = 20) -> List[CallLog]:
        """
        Get scheduled calls ordered by start time.
        """
        return self.db.query(CallLog).filter(
            CallLog.gym_id == tenant_id,
            CallLog.status == "scheduled",
            CallLog.start_time > datetime.utcnow()
        ).order_by(
            CallLog.start_time
        ).limit(limit).all()
    
    def get_call_with_transcript(self, call_id: UUID, tenant_id: UUID) -> Optional[CallLog]:
        """
        Get a call with its transcript eager-loaded.
        """
        return self.db.query(CallLog).options(
            joinedload(CallLog.transcript)
        ).filter(
            CallLog.id == call_id,
            CallLog.gym_id == tenant_id
        ).first()
    
    def get_calls_by_lead(self, lead_id: UUID, tenant_id: UUID) -> List[CallLog]:
        """
        Get all calls for a specific lead.
        """
        return self.db.query(CallLog).filter(
            CallLog.lead_id == lead_id,
            CallLog.gym_id == tenant_id
        ).order_by(
            CallLog.start_time.desc()
        ).all()
    
    def update_call_status(self, call_id: UUID, status: str, tenant_id: UUID) -> Optional[CallLog]:
        """
        Update a call's status.
        """
        call = self.get_by_id(call_id, tenant_id)
        if not call:
            return None
            
        call.status = status
        if status == "completed" and call.start_time and not call.end_time:
            call.end_time = datetime.utcnow()
            if call.start_time:
                call.duration = int((call.end_time - call.start_time).total_seconds())
                
        self.db.flush()
        return call
    
    def get_call_metrics(self, tenant_id: UUID, start_date: date, end_date: date) -> Dict[str, Any]:
        """
        Get call metrics for a date range.
        """
        # Get call outcome distribution
        outcome_results = self.db.query(
            CallLog.outcome,
            func.count(CallLog.id).label('count')
        ).filter(
            CallLog.gym_id == tenant_id,
            CallLog.start_time >= start_date,
            CallLog.start_time <= end_date,
            CallLog.outcome.isnot(None)
        ).group_by(
            CallLog.outcome
        ).all()
        
        outcomes = {outcome: 0 for outcome in ["appointment_booked", "follow_up_needed", "not_interested", "wrong_number", "voicemail", "no_answer", "other"]}
        for outcome, count in outcome_results:
            if outcome:
                outcomes[outcome] = count
                
        # Get average call duration
        duration_result = self.db.query(
            func.avg(CallLog.duration).label('avg_duration')
        ).filter(
            CallLog.gym_id == tenant_id,
            CallLog.start_time >= start_date,
            CallLog.start_time <= end_date,
            CallLog.duration.isnot(None)
        ).scalar()
        
        avg_duration = int(duration_result) if duration_result else 0
        
        # Get total calls
        total_calls = self.db.query(func.count(CallLog.id)).filter(
            CallLog.gym_id == tenant_id,
            CallLog.start_time >= start_date,
            CallLog.start_time <= end_date
        ).scalar()
        
        return {
            "total_calls": total_calls,
            "avg_duration": avg_duration,
            "outcomes": outcomes
        }
```

Common issues:
- Datetime handling
- Null value handling in aggregations
- Complex join performance

#### Appointment Repository

Located at `backend/db/repositories/appointment/appointment_repository.py`:

(Future application after completion of MVP)
```python
class AppointmentRepository(BaseRepository[Appointment]):
    """
    Repository for Appointment entity with specialized query methods.
    """
    
    def __init__(self, db_session: Session):
        super().__init__(db_session, Appointment)
    
    def get_upcoming_appointments(self, tenant_id: UUID, limit: int = 20) -> List[Appointment]:
        """
        Get upcoming appointments ordered by scheduled time.
        """
        return self.db.query(Appointment).filter(
            Appointment.gym_id == tenant_id,
            Appointment.scheduled_time > datetime.utcnow(),
            Appointment.status.in_(["scheduled", "confirmed"])
        ).order_by(
            Appointment.scheduled_time
        ).limit(limit).all()
    
    def get_appointments_for_lead(self, lead_id: UUID, tenant_id: UUID) -> List[Appointment]:
        """
        Get all appointments for a specific lead.
        """
        return self.db.query(Appointment).filter(
            Appointment.lead_id == lead_id,
            Appointment.gym_id == tenant_id
        ).order_by(
            Appointment.scheduled_time.desc()
        ).all()
    
    def check_conflicts(self, 
                        scheduled_time: datetime, 
                        end_time: datetime, 
                        staff_id: UUID, 
                        tenant_id: UUID,
                        exclude_id: Optional[UUID] = None) -> bool:
        """
        Check if there are any scheduling conflicts for a staff member.
        """
        query = self.db.query(Appointment).filter(
            Appointment.gym_id == tenant_id,
            Appointment.staff_id == staff_id,
            Appointment.status.in_(["scheduled", "confirmed"]),
            or_(
                # New appointment starts during existing
                and_(
                    Appointment.scheduled_time <= scheduled_time,
                    Appointment.end_time >= scheduled_time
                ),
                # New appointment ends during existing
                and_(
                    Appointment.scheduled_time <= end_time,
                    Appointment.end_time >= end_time
                ),
                # New appointment overlaps existing
                and_(
                    Appointment.scheduled_time >= scheduled_time,
                    Appointment.end_time <= end_time
                )
            )
        )
        
        # Exclude current appointment in case of update
        if exclude_id:
            query = query.filter(Appointment.id != exclude_id)
            
        return query.count() > 0
    
    def update_status(self, appointment_id: UUID, status: str, tenant_id: UUID) -> Optional[Appointment]:
        """
        Update an appointment's status.
        """
        appointment = self.get_by_id(appointment_id, tenant_id)
        if not appointment:
            return None
            
        appointment.status = status
        self.db.flush()
        return appointment
    
    def get_appointment_stats(self, tenant_id: UUID, start_date: date, end_date: date) -> Dict[str, int]:
        """
        Get appointment statistics for a date range.
        """
        results = self.db.query(
            Appointment.status,
            func.count(Appointment.id).label('count')
        ).filter(
            Appointment.gym_id == tenant_id,
            Appointment.scheduled_time >= start_date,
            Appointment.scheduled_time <= end_date
        ).group_by(
            Appointment.status
        ).all()
        
        # Convert to dictionary
        stats = {status: 0 for status in ["scheduled", "confirmed", "completed", "cancelled", "no_show"]}
        for status, count in results:
            stats[status] = count
            
        return stats
```

Common issues:
- Complex scheduling conflict queries
- Date/time range handling
- Status transition validation

## Query Patterns

### Tenant Isolation

All repositories implement tenant isolation through the `gym_id` filter:

```python
def get_by_id(self, entity_id: UUID, tenant_id: Optional[UUID] = None) -> Optional[T]:
    """Get an entity by ID with optional tenant filtering."""
    query = self.db.query(self.model_class).filter(self.model_class.id == entity_id)
    
    if tenant_id is not None and hasattr(self.model_class, 'gym_id'):
        query = query.filter(self.model_class.gym_id == tenant_id)
        
    return query.first()
```

Common issues:
- Missing tenant filters leading to data leakage
- Inconsistent tenant ID parameter naming
- Handling entities without tenant association

### Eager Loading

For performance optimization, relationships are eager-loaded as needed:

```python
def get_with_relationships(self, lead_id: UUID, tenant_id: UUID) -> Optional[Lead]:
    """
    Get a lead with eager-loaded relationships.
    """
    return self.db.query(Lead).options(
        joinedload(Lead.qualification),
        joinedload(Lead.tags),
        joinedload(Lead.calls),
        joinedload(Lead.appointments)
    ).filter(
        Lead.id == lead_id,
        Lead.gym_id == tenant_id
    ).first()
```

Common issues:
- Over-eager loading causing performance issues
- N+1 query patterns when loading relationships
- Missing relationships in eager loads

### Pagination, Filtering, and Sorting

Standardized pagination, filtering, and sorting are provided by the base repository:

```python
def list(self, 
         tenant_id: Optional[UUID] = None, 
         skip: int = 0, 
         limit: int = 100,
         filters: Optional[Dict[str, Any]] = None,
         sort_by: Optional[str] = None,
         sort_dir: Optional[str] = None) -> List[T]:
    """
    List entities with pagination, filtering, and sorting.
    Automatically applies tenant isolation if applicable.
    """
    query = self.db.query(self.model_class)
    
    # Apply tenant isolation
    if tenant_id is not None and hasattr(self.model_class, 'gym_id'):
        query = query.filter(self.model_class.gym_id == tenant_id)
    
    # Apply custom filters
    if filters:
        query = self._apply_filters(query, filters)
    
    # Apply sorting
    if sort_by:
        query = self._apply_sorting(query, sort_by, sort_dir)
    
    # Apply pagination
    return query.offset(skip).limit(limit).all()
```

Common issues:
- Large offset values causing performance issues
- Complex filter combinations
- Sorting by computed or related fields

## Caching Integration

Repositories can integrate with caching through decorators:

```python
class CachedLeadRepository(LeadRepository):
    """
    Lead repository with caching capabilities.
    """
    
    @repository_cache(ttl=300)
    def get_prioritized_leads(self, tenant_id: UUID, limit: int = 20) -> List[Lead]:
        """
        Get leads ordered by priority score for a specific tenant.
        This method is cached with a 5-minute TTL.
        """
        return super().get_prioritized_leads(tenant_id, limit)
    
    @repository_cache(ttl=3600)
    def get_lead_conversion_stats(self, tenant_id: UUID, start_date: date, end_date: date) -> Dict[str, int]:
        """
        Get lead conversion statistics for a date range.
        This method is cached with a 1-hour TTL.
        """
        return super().get_lead_conversion_stats(tenant_id, start_date, end_date)
    
    def create(self, data: Dict[str, Any], tenant_id: Optional[UUID] = None) -> Lead:
        """
        Create a lead and invalidate related caches.
        """
        lead = super().create(data, tenant_id)
        
        # Invalidate caches that may be affected
        cache_invalidation_manager.invalidate(
            f"lead_repository:get_prioritized_leads:{tenant_id}"
        )
        
        return lead
```

Common issues:
- Cache key design
- Inconsistent invalidation patterns
- Over-caching mutable data

## Transaction Management

Repositories operate within transaction contexts managed by the service layer:

```python
# In service implementation
def create_appointment_with_notification(self, data: AppointmentCreate, user_id: UUID) -> Appointment:
    try:
        # Start transaction
        self.db.begin()
        
        # Create appointment using repository
        appointment = self.appointment_repository.create(data.__dict__, user_id)
        
        # Schedule notification
        self.notification_service.schedule_appointment_notification(appointment.id)
        
        # Commit transaction
        self.db.commit()
        return appointment
    except Exception as e:
        # Rollback on error
        self.db.rollback()
        raise e
```

Common issues:
- Transaction leakage
- Missing rollback on exceptions
- Nested transaction management

## Raw SQL Queries

For complex queries, repositories can use raw SQL:

```python
def get_lead_analytics_dashboard(self, tenant_id: UUID) -> Dict[str, Any]:
    """
    Get comprehensive lead analytics using raw SQL for optimization.
    """
    query = text("""
        WITH lead_counts AS (
            SELECT 
                status,
                COUNT(*) as count
            FROM lead
            WHERE gym_id = :tenant_id
            GROUP BY status
        ),
        daily_leads AS (
            SELECT 
                DATE(created_at) as date,
                COUNT(*) as count
            FROM lead
            WHERE 
                gym_id = :tenant_id AND
                created_at >= DATE(NOW()) - INTERVAL '30 days'
            GROUP BY DATE(created_at)
            ORDER BY date
        ),
        conversion_rates AS (
            SELECT 
                source,
                COUNT(*) as total,
                SUM(CASE WHEN status = 'converted' THEN 1 ELSE 0 END) as converted,
                (SUM(CASE WHEN status = 'converted' THEN 1 ELSE 0 END) * 100.0 / COUNT(*)) as rate
            FROM lead
            WHERE gym_id = :tenant_id
            GROUP BY source
            HAVING COUNT(*) > 10
        )
        SELECT 
            json_build_object(
                'lead_counts', (SELECT json_object_agg(status, count) FROM lead_counts),
                'daily_leads', (SELECT json_agg(daily_leads) FROM daily_leads),
                'conversion_rates', (SELECT json_agg(conversion_rates) FROM conversion_rates)
            ) as result
    """)
    
    result = self.db.execute(query, {"tenant_id": tenant_id}).scalar()
    return json.loads(result) if result else {}
```

Common issues:
- Database dialect compatibility
- Parameter binding
- Query performance optimization

## Performance Optimization

The repository layer implements several performance strategies:

### 1. Indexing

Database models include indexes for frequently queried fields:

```python
class Lead(BaseModel):
    __tablename__ = "lead"
    
    # Indexed fields for frequent queries
    gym_id = Column(UUID(as_uuid=True), ForeignKey("gym.id", ondelete="CASCADE"), nullable=False, index=True)
    phone = Column(String(20), nullable=False, index=True)
    email = Column(String(255), nullable=True, index=True)
    
    # Compound index for frequent queries
    __table_args__ = (
        Index('ix_lead_gym_status', 'gym_id', 'status'),
    )
```

Common issues:
- Missing indexes on frequent query fields
- Over-indexing causing write performance issues
- Inappropriate compound indexes

### 2. Query Optimization

Complex queries are optimized for performance:

```python
def get_prioritized_leads(self, tenant_id: UUID, limit: int = 20) -> List[Lead]:
    """
    Optimized query for lead prioritization.
    """
    return self.db.query(Lead).options(
        # Use lazyload to avoid fetching unneeded relationships
        lazyload(Lead.calls),
        lazyload(Lead.appointments),
        # Only eager load what's needed for prioritization
        joinedload(Lead.qualification)
    ).join(
        LeadQualification, 
        Lead.id == LeadQualification.lead_id
    ).filter(
        Lead.gym_id == tenant_id,
        Lead.status.in_(["new", "contacted", "qualified"])
    ).order_by(
        desc(LeadQualification.score),
        Lead.created_at.desc()
    ).limit(limit).all()
```

Common issues:
- Cartesian products in joins
- Missing or inappropriate eager/lazy loading
- Inefficient filter ordering

### 3. Result Caching

Repositories use caching for frequently accessed results:

```python
@repository_cache(ttl=300)
def get_lead_conversion_stats(self, tenant_id: UUID, start_date: date, end_date: date) -> Dict[str, int]:
    """Get lead conversion statistics with caching."""
    # Implementation
```

Common issues:
- Inappropriate TTL for data volatility
- Missing cache invalidation
- Cache key collisions

## Testing Approach

The repository layer is designed for testability:

```python
# Repository unit test example
def test_lead_repository_get_prioritized_leads():
    # Setup in-memory database
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    
    # Create session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Set up test data
        gym_id = uuid.uuid4()
        gym = Gym(id=gym_id, name="Test Gym")
        db.add(gym)
        
        # Create leads with different qualification scores
        leads = []
        for i in range(5):
            lead = Lead(
                gym_id=gym_id,
                first_name=f"Test{i}",
                last_name=f"User{i}",
                phone=f"123456789{i}",
                status="qualified"
            )
            db.add(lead)
            leads.append(lead)
            
            # Add qualification with different scores
            qualification = LeadQualification(
                lead_id=lead.id,
                score=i * 10
            )
            db.add(qualification)
        
        db.commit()
        
        # Create repository
        repository = LeadRepository(db)
        
        # Test prioritized leads
        result = repository.get_prioritized_leads(gym_id, limit=3)
        
        # Verify results
        assert len(result) == 3
        # Leads should be ordered by qualification score (descending)
        assert result[0].id == leads[4].id  # Highest score
        assert result[1].id == leads[3].id
        assert result[2].id == leads[2].id
        
    finally:
        db.close()
```

Common testing patterns:
- In-memory database testing
- Fixture-based test data setup
- Transaction isolation between tests
- Mock databases for unit testing

## Common Repository Issues

### 1. N+1 Query Problem

When accessing relationships individually instead of using eager loading:

```python
# Problematic code causing N+1 queries
leads = lead_repository.list(tenant_id)
for lead in leads:
    # This causes a separate query for each lead
    calls = lead.calls
    print(f"Lead {lead.id} has {len(calls)} calls")

# Corrected approach with eager loading
leads = lead_repository.list(tenant_id, options=[joinedload(Lead.calls)])
for lead in leads:
    # No additional queries needed
    calls = lead.calls
    print(f"Lead {lead.id} has {len(calls)} calls")
```

### 2. Transaction Management Issues

```python
# Problematic transaction leakage
def process_leads(self):
    self.db.begin()
    try:
        # Process leads
        for lead in self.lead_repository.list(...):
            self.process_lead(lead)  # This might start a nested transaction
            
        self.db.commit()
    except:
        self.db.rollback()
        raise

# Corrected approach with context manager
def process_leads(self):
    with self.db.begin() as transaction:
        # Process leads
        for lead in self.lead_repository.list(...):
            self.process_lead(lead)
        # Automatically commits or rollbacks
```

### 3. Missing Tenant Isolation

```python
# Problematic code missing tenant isolation
def get_lead_by_phone(self, phone: str):
    # Missing tenant filter could leak data across tenants
    return self.db.query(Lead).filter(Lead.phone == phone).first()

# Corrected approach with tenant isolation
def get_lead_by_phone(self, phone: str, tenant_id: UUID):
    return self.db.query(Lead).filter(
        Lead.phone == phone,
        Lead.gym_id == tenant_id
    ).first()
```

### 4. Inefficient Query Patterns

```python
# Problematic inefficient filtering
def get_leads_by_status(self, statuses: List[str], tenant_id: UUID):
    result = []
    # Inefficient: multiple queries
    for status in statuses:
        leads = self.db.query(Lead).filter(
            Lead.status == status,
            Lead.gym_id == tenant_id
        ).all()
        result.extend(leads)
    return result

# Corrected approach with single query
def get_leads_by_status(self, statuses: List[str], tenant_id: UUID):
    return self.db.query(Lead).filter(
        Lead.status.in_(statuses),
        Lead.gym_id == tenant_id
    ).all()
```

## Repository Lifecycle Management

### Connection Pooling

The database layer implements connection pooling for optimal performance:

```python
class DatabasePool:
    """Manages SQLAlchemy connection pools for efficient database access."""
    
    _instance = None
    
    @classmethod
    def get_instance(cls) -> 'DatabasePool':
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = DatabasePool()
        return cls._instance
    
    def __init__(self):
        """Initialize connection pools."""
        self.engine = create_engine(
            settings.DATABASE_URL,
            pool_size=settings.DB_POOL_SIZE,
            max_overflow=settings.DB_MAX_OVERFLOW,
            pool_timeout=settings.DB_POOL_TIMEOUT,
            pool_recycle=settings.DB_POOL_RECYCLE
        )
        self.session_factory = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
        
    def get_session(self) -> Session:
        """Get a new database session from the pool."""
        return self.session_factory()
```

Common issues:
- Connection pool exhaustion during traffic spikes
- Connections not properly returned to the pool
- Pool sizing misconfiguration

### Session Management

Sessions are managed through dependency injection and context managers:

```python
def get_db() -> Generator[Session, None, None]:
    """Dependency for database sessions."""
    db = DatabasePool.get_instance().get_session()
    try:
        yield db
        db.commit()
    except:
        db.rollback()
        raise
    finally:
        db.close()
```

Common issues:
- Session leaks in error scenarios
- Long-running sessions blocking pool capacity
- Missing explicit commits or rollbacks

### Repository Initialization

Repositories are typically initialized with database sessions:

```python
class LeadServiceFactory:
    @staticmethod
    def create(db_session: Session) -> ILeadService:
        # Initialize repositories with session
        lead_repository = LeadRepository(db_session)
        
        # Create service with repository
        return LeadService(lead_repository)
```

Common issues:
- Using different sessions for related repositories
- Repository initialization outside transaction boundaries
- Missing session cleanup

## Repository Factory Pattern

The repository layer implements factories to manage repository creation and dependencies:

```python
class RepositoryFactory:
    """Factory for creating repository instances with proper dependencies."""
    
    @staticmethod
    def create_lead_repository(db_session: Session) -> ILeadRepository:
        """Create a LeadRepository instance."""
        # Choose implementation type based on configuration
        if settings.USE_CACHED_REPOSITORIES:
            return CachedLeadRepository(db_session)
        return LeadRepository(db_session)
    
    @staticmethod
    def create_call_repository(db_session: Session) -> ICallRepository:
        """Create a CallRepository instance."""
        if settings.USE_CACHED_REPOSITORIES:
            return CachedCallRepository(db_session)
        return CallRepository(db_session)
        
    # Additional factory methods for other repositories
```

Common issues:
- Inconsistent implementation selection
- Missing repository type validation
- Repository configuration gaps

### Repository Registration

For dependency injection systems, repositories can be registered:

```python
def register_repositories(container):
    """Register repositories with the dependency injection container."""
    container.register(ILeadRepository, 
                      lambda c: RepositoryFactory.create_lead_repository(c.resolve(Session)))
    container.register(ICallRepository, 
                      lambda c: RepositoryFactory.create_call_repository(c.resolve(Session)))
    # Register other repositories
```

Common issues:
- Circular dependencies between repositories
- Inconsistent registration patterns
- Missing repository registrations

## Cache Invalidation Strategies

The repository layer implements cache invalidation at multiple levels:

### Key-based Invalidation

Cache keys are carefully designed for targeted invalidation:

```python
def get_lead_conversion_stats(self, tenant_id: UUID, start_date: date, end_date: date) -> Dict[str, int]:
    """Get lead conversion statistics with caching."""
    # Generate cache key with all parameters
    cache_key = f"lead:stats:{tenant_id}:{start_date}:{end_date}"
    
    # Try to get from cache
    cached_result = self.cache.get(cache_key)
    if cached_result:
        return cached_result
    
    # If not in cache, query database
    results = self.db.query(
        Lead.status,
        func.count(Lead.id).label('count')
    ).filter(
        Lead.gym_id == tenant_id,
        Lead.created_at >= start_date,
        Lead.created_at <= end_date
    ).group_by(
        Lead.status
    ).all()
    
    # Process results
    stats = {status: 0 for status in ["new", "contacted", "qualified", "converted", "lost"]}
    for status, count in results:
        stats[status] = count
    
    # Store in cache
    self.cache.set(cache_key, stats, ttl=3600)  # 1 hour TTL
    
    return stats
```

### Pattern-based Invalidation

When data changes affect multiple cached items, pattern invalidation is used:

```python
def create(self, data: Dict[str, Any], tenant_id: Optional[UUID] = None) -> Lead:
    """Create a lead and invalidate related caches."""
    # Create lead
    entity = super().create(data, tenant_id)
    
    # Invalidate all lead statistics caches for this tenant
    self.cache.delete_pattern(f"lead:stats:{tenant_id}:*")
    
    # Invalidate prioritized leads cache
    self.cache.delete(f"lead:prioritized:{tenant_id}")
    
    return entity
```

### Dependent Cache Invalidation

For complex relationships, cascading invalidation is implemented:

```python
def update_lead_status(self, lead_id: UUID, status: str, tenant_id: UUID) -> Optional[Lead]:
    """Update lead status and invalidate dependent caches."""
    # Update lead
    lead = super().update(lead_id, {"status": status}, tenant_id)
    if not lead:
        return None
    
    # Invalidate lead cache
    self.cache.delete(f"lead:{lead_id}")
    
    # Invalidate dependent caches
    self.cache.delete_pattern(f"lead:stats:{tenant_id}:*")  # Lead statistics
    self.cache.delete(f"lead:prioritized:{tenant_id}")      # Prioritized leads
    
    # Invalidate related entity caches
    if lead.calls:
        for call in lead.calls:
            self.cache.delete(f"call:{call.id}")
    
    return lead
```

Common issues:
- Over-invalidation causing cache thrashing
- Under-invalidation leading to stale data
- Complex invalidation patterns hard to maintain

## Data Migration and Versioning

### Alembic Integration

The repository layer interacts with Alembic for database migrations:

```python
# In alembic/env.py
from backend.db.models.base import Base
from backend.db.models import *  # Import all models

# Register models with Alembic
target_metadata = Base.metadata
```

### Model Versioning Strategies

For handling model changes:

```python
class LeadV2(BaseModel):
    """New version of Lead model with additional fields."""
    __tablename__ = "lead"
    
    # Original fields
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    gym_id = Column(UUID(as_uuid=True), ForeignKey("gym.id", ondelete="CASCADE"), nullable=False, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    
    # New fields
    engagement_score = Column(Integer, nullable=True)
    last_interaction = Column(DateTime, nullable=True)
    
    # Handle legacy records
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.engagement_score is None:
            # Apply default calculation for legacy records
            self.engagement_score = 0
```

### Migration Best Practices

Guidelines for safe database migrations:
1. **Run automated tests** before and after migrations
2. **Use transactions** to make migrations atomic
3. **Implement rollback mechanisms** for failed migrations
4. **Perform on non-peak hours** to minimize impact
5. **Test migrations in staging** before production

Common migration issues:
- Data corruption during schema changes
- Performance impacts during large migrations
- Application compatibility with schema changes

## Monitoring and Instrumentation

The repository layer includes monitoring for performance and diagnostics:

### Query Timing

```python
def list(self, 
         tenant_id: Optional[UUID] = None, 
         skip: int = 0, 
         limit: int = 100,
         filters: Optional[Dict[str, Any]] = None,
         sort_by: Optional[str] = None,
         sort_dir: Optional[str] = None) -> List[T]:
    """List entities with performance monitoring."""
    # Start timing
    start_time = time.time()
    
    # Build query
    query = self.db.query(self.model_class)
    
    # Apply filters and execute
    # ... existing implementation ...
    
    # Record query time
    query_time = time.time() - start_time
    logger.debug(f"Repository query executed in {query_time:.4f}s: {self.model_class.__name__}.list")
    
    # Record metrics if query time exceeds threshold
    if query_time > settings.SLOW_QUERY_THRESHOLD:
        metrics.record_slow_query(
            model=self.model_class.__name__,
            method="list",
            parameters={"tenant_id": tenant_id, "filters": filters},
            duration=query_time
        )
    
    return result
```

### Cache Effectiveness

```python
def get_by_id(self, entity_id: UUID, tenant_id: Optional[UUID] = None) -> Optional[T]:
    """Get entity by ID with cache metrics."""
    cache_key = f"{self.model_class.__name__}:{entity_id}"
    
    # Attempt to get from cache
    cached = self.cache.get(cache_key)
    if cached:
        metrics.increment("repository.cache.hit", tags=[self.model_class.__name__])
        return cached
    
    # Cache miss, query database
    metrics.increment("repository.cache.miss", tags=[self.model_class.__name__])
    
    # Execute query
    # ... existing implementation ...
    
    # Update cache
    if entity:
        self.cache.set(cache_key, entity, ttl=settings.ENTITY_CACHE_TTL)
    
    return entity
```

### Health Checks

```python
def perform_health_check(self) -> Dict[str, Any]:
    """Check database health and performance."""
    results = {
        "status": "healthy",
        "issues": []
    }
    
    try:
        # Check connection
        start_time = time.time()
        self.db.execute(text("SELECT 1"))
        connection_time = time.time() - start_time
        
        results["connection_time_ms"] = int(connection_time * 1000)
        
        # Check pool usage
        pool_info = inspect(self.db.get_bind()).pool.status()
        results["pool_status"] = {
            "checkedout": pool_info["checkedout"],
            "checkedin": pool_info["checkedin"],
            "size": pool_info["pool_size"],
            "overflow": pool_info["overflow"],
        }
        
        # Set warning if pool usage is high
        if pool_info["checkedout"] > pool_info["pool_size"] * 0.8:
            results["issues"].append("High connection pool usage")
            
    except Exception as e:
        results["status"] = "unhealthy"
        results["issues"].append(str(e))
    
    return results
```

Common monitoring issues:
- Missing instrumentation for critical queries
- Excessive logging affecting performance
- Inadequate alerting for database issues

## Conclusion

The Database Repository Layer in the Reps AI Dashboard Backend provides a clean abstraction for data access with strong multi-tenant isolation, performance optimization, and business rule enforcement. By following the Repository Pattern, it simplifies database interactions while maintaining flexibility for different query patterns and optimizations.