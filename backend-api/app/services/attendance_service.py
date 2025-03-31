# app/services/attendance_service.py
from fastapi import HTTPException
from datetime import datetime
import logging
import time
from typing import Dict, List, Any, Optional
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import psycopg2

from app.models import AttendanceEntry
from app.config import settings

# Configure logging
logger = logging.getLogger(__name__)

# Define retry decorator for database operations
db_retry = retry(
    stop=stop_after_attempt(settings.DB_RETRY_ATTEMPTS),
    wait=wait_exponential(multiplier=1, min=settings.DB_RETRY_MIN_SECONDS, max=settings.DB_RETRY_MAX_SECONDS),
    retry=retry_if_exception_type((psycopg2.OperationalError, psycopg2.InterfaceError)),
    reraise=True
)

@db_retry
def add_attendance(conn, entry: AttendanceEntry) -> Dict[str, str]:
    """
    Add a new attendance entry to the database
    
    Args:
        conn: Database connection
        entry: AttendanceEntry model containing attendance data
        
    Returns:
        Dict with success message
        
    Raises:
        HTTPException: If there's an error adding the entry
    """
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO attendance (employee_id, date, status, department) VALUES (%s, %s, %s, %s)",
            (entry.employee_id, entry.date, entry.status, entry.department)
        )
        return {"message": "Attendance added successfully"}
    except psycopg2.IntegrityError as e:
        logger.error(f"Integrity error adding attendance: {str(e)}")
        raise HTTPException(status_code=409, detail=f"Attendance record already exists or violates constraints")
    except Exception as e:
        logger.error(f"Error adding attendance: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to add attendance: {str(e)}")

@db_retry
def update_attendance(conn, entry: AttendanceEntry) -> Dict[str, str]:
    """
    Update an existing attendance entry
    
    Args:
        conn: Database connection
        entry: AttendanceEntry model containing updated attendance data
        
    Returns:
        Dict with success message
        
    Raises:
        HTTPException: If record not found or there's an error updating the entry
    """
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE attendance
            SET status = %s, department = %s
            WHERE employee_id = %s AND date = %s
        """, (entry.status, entry.department, entry.employee_id, entry.date))
        
        if cursor.rowcount == 0:
            logger.warning(f"No attendance record found for employee {entry.employee_id} on {entry.date}")
            raise HTTPException(status_code=404, detail="Attendance record not found")
        
        return {"message": "Attendance updated successfully"}
    except psycopg2.IntegrityError as e:
        logger.error(f"Integrity error updating attendance: {str(e)}")
        raise HTTPException(status_code=409, detail=f"Update violates data constraints")
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error updating attendance: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update attendance: {str(e)}")

@db_retry
def get_attendance_trends(conn) -> Dict[int, Dict[str, Any]]:
    """
    Get attendance trends for all employees
    
    Args:
        conn: Database connection
        
    Returns:
        Dict with employee attendance stats
        
    Raises:
        HTTPException: If there's an error fetching the data
    """
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT employee_id, department, status, COUNT(*) FROM attendance GROUP BY department, employee_id, status"
        )
        records = cursor.fetchall()
        
        trends = {}
        for record in records:
            emp_id = record['employee_id']
            department = record['department']
            status = record['status']
            count = record['count']
            
            if emp_id not in trends:
                trends[emp_id] = {"department": department, "attendance": {}}
            trends[emp_id]["attendance"][status] = count
            
        return trends
    except Exception as e:
        logger.error(f"Error getting attendance trends: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get attendance trends: {str(e)}")

@db_retry
def get_employee_attendance(conn, employee_id: int) -> List[Dict[str, Any]]:
    """
    Get attendance records for a specific employee
    
    Args:
        conn: Database connection
        employee_id: ID of the employee
        
    Returns:
        List of attendance records
        
    Raises:
        HTTPException: If there's an error fetching the data
    """
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM attendance WHERE employee_id = %s ORDER BY date DESC",
            (employee_id,)
        )
        return cursor.fetchall()
    except Exception as e:
        logger.error(f"Error getting employee attendance: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get employee attendance: {str(e)}")