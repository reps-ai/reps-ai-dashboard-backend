from pydantic import BaseModel
from typing import List

class ImportMapping(BaseModel):
    first_name: str
    last_name: str
    phone: str
    email: str
    status: str
    interest: str
    branch_id: str
    source: str

class ImportDefaultValues(BaseModel):
    status: str
    branch_id: str
    source: str

class ImportRequest(BaseModel):
    mapping: ImportMapping
    default_values: ImportDefaultValues

class ImportResponse(BaseModel):
    job_id: str
    total_records: int
    status: str

class ImportError(BaseModel):
    row: int
    message: str

class ImportJobStatus(BaseModel):
    job_id: str
    status: str
    total_records: int
    processed: int
    successful: int
    failed: int
    errors: List[ImportError] = [] 