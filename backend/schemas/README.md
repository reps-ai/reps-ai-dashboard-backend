# Data Schemas

## Overview

This directory contains Pydantic models for data validation and serialization across the AI Dashboard backend. The schemas define the structure and validation rules for all data objects in the system, ensuring data consistency and type safety.

## Directory Structure

```
schemas/
├── __init__.py
├── analytics/          # Analytics data models
│   ├── models.py
│   └── enhanced_models.py
├── appointments/       # Appointment schemas
│   └── models.py
├── calls/             # Call handling schemas
│   ├── models.py
│   └── enhanced_models.py
├── common/            # Shared schemas and utilities
│   ├── base.py
│   ├── enums.py
│   ├── responses.py
│   └── validators.py
├── leads/             # Lead management schemas
│   ├── models.py
│   └── enhanced_models.py
└── settings/          # Configuration schemas
    └── models.py
```

## Common Patterns

### Base Models

Common base models and mixins are defined in `common/base.py`:

```python
class TimestampMixin(BaseModel):
    created_at: datetime
    updated_at: Optional[datetime] = None

class ServiceResponse(BaseModel):
    success: bool
    message: str
```

### Model Structure

Each domain follows a consistent pattern:

1. Base Model:

   - Core fields
   - Validation rules
   - Common behavior

2. Create Model:

   - Fields required for creation
   - Additional validation

3. Update Model:

   - Optional fields
   - Partial updates

4. DB Model:
   - Database representation
   - Additional metadata
   - Timestamp fields

Example:

```python
class LeadBase(BaseModel):
    first_name: str
    last_name: str
    email: Optional[EmailStr]

class LeadCreate(LeadBase):
    # Additional creation fields
    pass

class LeadUpdate(BaseModel):
    # Optional fields for updates
    first_name: Optional[str]

class LeadInDB(LeadBase, TimestampMixin):
    id: str
    # Additional DB fields
```

## Validation Rules

### Field Validation

```python
class ExampleModel(BaseModel):
    name: str = Field(..., min_length=1)
    score: float = Field(..., ge=0, le=100)
    email: EmailStr
    status: Status = Status.ACTIVE
```

### Custom Validators

```python
class PhoneModel(BaseModel):
    phone: str

    @validator('phone')
    def validate_phone(cls, v):
        cleaned = ''.join(filter(str.isdigit, v))
        if not (10 <= len(cleaned) <= 15):
            raise ValueError('Invalid phone number')
        return v
```

## Domain Schemas

### Analytics Models

- Metric definitions
- Report structures
- Analysis results

### Appointment Models

- Scheduling data
- Availability slots
- Booking information

### Call Models

- Call metadata
- Recording information
- Call outcomes

### Lead Models

- Contact information
- Lead status tracking
- Qualification data

### Settings Models

- System configurations
- User preferences
- Integration settings

## Enumerations

Common enums are defined in `common/enums.py`:

```python
class LeadSource(str, Enum):
    WEBSITE = "website"
    REFERRAL = "referral"
    DIRECT = "direct"
    SOCIAL = "social"
    OTHER = "other"

class Status(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
```

## Response Models

Standard response models in `common/responses.py`:

```python
class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    size: int

class ErrorResponse(BaseModel):
    code: str
    message: str
    details: Optional[Dict[str, Any]]
```

## Best Practices

### 1. Model Design

- Use descriptive field names
- Include field descriptions
- Set appropriate constraints
- Use type hints
- Add validation rules
- Document edge cases

### 2. Validation

- Validate at model level
- Use custom validators
- Add meaningful error messages
- Handle edge cases
- Validate data types

### 3. Documentation

- Document all models
- Include examples
- Document validation rules
- Add field descriptions
- Note required fields

### 4. Inheritance

- Use base models
- Share common fields
- Use mixins
- Keep hierarchy simple
- Document relationships

## Development Guidelines

### Adding New Models

1. Choose appropriate domain
2. Create base model
3. Add validation rules
4. Create derived models
5. Add documentation
6. Add tests

### Modifying Models

1. Consider backwards compatibility
2. Update validations
3. Update documentation
4. Update tests
5. Check dependencies

## Testing

### Model Testing

```python
def test_model_validation():
    model = ExampleModel(
        name="Test",
        score=50
    )
    assert model.name == "Test"
    assert model.score == 50
```

### Validation Testing

```python
def test_phone_validation():
    with pytest.raises(ValidationError):
        PhoneModel(phone="invalid")
```

## Dependencies

- pydantic: Data validation
- email-validator: Email validation
- datetime: Date/time fields
- typing: Type hints
- enum: Enumerations
