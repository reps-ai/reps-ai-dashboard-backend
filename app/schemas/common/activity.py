from pydantic import BaseModel

class Call(BaseModel):
    id: str
    direction: str
    status: str
    start_time: str
    duration: int
    outcome: str
    sentiment: str
    summary: str

class Appointment(BaseModel):
    id: str
    type: str
    date: str
    duration: int
    status: str
    branch_name: str 