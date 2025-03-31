# app/models.py
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
import re

class AttendanceEntry(BaseModel):
    employee_id: int = Field(..., gt=0, description="Employee ID (positive integer)")
    date: str = Field(..., description="Attendance date in format YYYY-MM-DD")
    status: str = Field(..., description="Attendance status (Present, Absent, WFH)")
    department: str = Field(..., min_length=1, max_length=50, description="Department name")

    @validator('date')
    def validate_date_format(cls, v):
        """Validate that the date is in YYYY-MM-DD format"""
        date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
        if not date_pattern.match(v):
            raise ValueError("Date must be in YYYY-MM-DD format")
        try:
            datetime.strptime(v, '%Y-%m-%d')
        except ValueError:
            raise ValueError("Invalid date")
        return v
    
    @validator('status')
    def validate_status(cls, v):
        """Validate that status is one of the allowed values"""
        allowed_statuses = ['Present', 'Absent', 'WFH']
        if v not in allowed_statuses:
            raise ValueError(f"Status must be one of {', '.join(allowed_statuses)}")
        return v

class InsightsRequest(BaseModel):
    user_query: Optional[str] = Field(
        None, 
        description="User's query for generating insights from attendance data"
    )