# Dependency Update Migration Guide

This guide outlines the steps to update the critical dependencies in the Reps-AI backend application. The updates focus on four major components: Pydantic, FastAPI, SQLAlchemy, and Uvicorn.

## Overview of Changes

| Package | Current Version | Updated Version | Breaking Changes |
|---------|----------------|----------------|------------------|
| Pydantic | 1.10.7 | 2.6.4 | Major API changes |
| FastAPI | 0.95.0 | 0.110.0 | Pydantic v2 compatibility |
| SQLAlchemy | 2.0.9 | 2.0.29 | Minor improvements |
| Uvicorn | 0.21.1 | 0.27.1 | Bug fixes and improvements |

## Testing Strategy

Before applying these changes to production, it's crucial to:

1. Create a dedicated testing/staging environment
2. Update one component at a time
3. Run comprehensive tests after each update
4. Document any issues encountered

## Migration Steps

### 1. SQLAlchemy Update (2.0.9 → 2.0.29)

This is the least disruptive update with minimal breaking changes.

#### Changes Required:
- Update version in requirements.txt
- Watch for any deprecation warnings
- Test database connections and queries

### 2. Uvicorn Update (0.21.1 → 0.27.1)

The Uvicorn update fixes several bugs, including a critical one where request.state persists between requests.

#### Changes Required:
- Update version in requirements.txt
- Test application startup and server behavior
- Verify HTTP connections and WebSocket functionality

### 3. Pydantic Update (1.10.7 → 2.6.4)

This is the most significant update, requiring careful migration of models.

#### Key API Changes:
- Validator decorators have changed: `@validator` → `@field_validator`
- JSON methods renamed: `model.dict()` → `model.model_dump()`
- Config class definition has changed
- Strict type validation is on by default

#### Examples:

**Before:**
```python
from pydantic import BaseModel, validator

class User(BaseModel):
    id: int
    name: str
    
    @validator('name')
    def validate_name(cls, v):
        if len(v) < 3:
            raise ValueError('Name must be at least 3 characters')
        return v
        
    class Config:
        orm_mode = True
```

**After:**
```python
from pydantic import BaseModel, field_validator, ConfigDict

class User(BaseModel):
    id: int
    name: str
    
    model_config = ConfigDict(from_attributes=True)
    
    @field_validator('name')
    def validate_name(cls, v):
        if len(v) < 3:
            raise ValueError('Name must be at least 3 characters')
        return v
```

#### Required Changes:
1. Update all Pydantic models in `app/schemas/`
2. Change validator decorators
3. Update model configuration
4. Change serialization methods (`dict()` → `model_dump()`)
5. Update imports

### 4. FastAPI Update (0.95.0 → 0.110.0)

FastAPI's update is primarily to be compatible with Pydantic v2.

#### Changes Required:
- Update version in requirements.txt
- Test all endpoints with the new Pydantic schema
- Verify response models and validation
- Check API documentation (Swagger/ReDoc)

## Specific Files to Update

### Pydantic Models:
- `app/dependencies.py` - Update User, Gym, and Branch models
- `app/schemas/auth.py` - Update UserCreate model
- All models in `app/schemas/leads/`, `app/schemas/calls/`, etc.

### FastAPI Routes:
- All route handlers that use Pydantic models for request/response
- Authentication handlers in `app/routes/auth/`

### SQLAlchemy Models:
- Consider using new typing features with `Mapped` and `mapped_column`
- Test all ORM operations

## Post-Migration Verification

After updating all dependencies, ensure:

1. API endpoints function correctly
2. Authentication works as expected
3. Database operations run without errors
4. WebSockets (if used) function properly
5. Background tasks execute correctly

## Rollback Plan

If issues arise that cannot be immediately resolved:

1. Document the specific issue and dependencies involved
2. Revert to the previous dependency versions
3. Create a separate branch for troubleshooting
4. Consider incremental updates with intermediate versions

## Additional Considerations

### Performance
- Pydantic v2 should be significantly faster than v1
- Monitor API response times before and after migration

### Error Handling
- Pydantic v2 may produce different validation errors
- Update error handling accordingly

### Documentation
- Update API documentation to reflect any changes
- Document new features that could be utilized

## Resources

- [Pydantic v2 Migration Guide](https://docs.pydantic.dev/latest/migration/)
- [FastAPI with Pydantic v2](https://fastapi.tiangolo.com/advanced/using-pydantic-v2/)
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [Uvicorn Changelog](https://github.com/encode/uvicorn/releases) 