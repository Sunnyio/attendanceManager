# main.py
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from typing import List, Dict, Any
import time
import logging
import traceback

from app.config import settings
from app.database import get_db, initialize_db
from app.models import AttendanceEntry, InsightsRequest
from app.services import attendance_service, ai_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Attendance API",
    description="API for tracking and analyzing employee attendance",
    version="1.0.0",
    swagger_ui_parameters={"syntaxHighlight": False}
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add middleware for request timing and logging
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        logger.info(f"Request to {request.url.path} completed in {process_time:.4f}s")
        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(f"Request to {request.url.path} failed after {process_time:.4f}s: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error", "error_type": type(e).__name__}
        )

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}")
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred", "error_type": type(exc).__name__}
    )

# Initialize the database
@app.on_event("startup")
async def startup_event():
    logger.info("Initializing database...")
    initialize_db()
    logger.info("API startup complete")

# API Endpoints
@app.post("/attendance/", response_model=Dict[str, str])
async def add_attendance(entry: AttendanceEntry, db=Depends(get_db)):
    """Add a new attendance entry to the database"""
    return attendance_service.add_attendance(db, entry)

@app.put("/attendance/", response_model=Dict[str, str])
async def update_attendance(entry: AttendanceEntry, db=Depends(get_db)):
    """Update an existing attendance entry"""
    return attendance_service.update_attendance(db, entry)

@app.get("/attendance/trends", response_model=Dict[str, Dict])
async def get_attendance_trends(db=Depends(get_db)):
    """Get attendance trends across departments and employees"""
    return {"attendance_trends": attendance_service.get_attendance_trends(db)}

@app.get("/attendance/{employee_id}", response_model=Dict[str, Any])
async def get_attendance(employee_id: int, db=Depends(get_db)):
    """Get attendance records for a specific employee"""
    attendance = attendance_service.get_employee_attendance(db, employee_id)
    if not attendance:
        return {"message": "No attendance found for employee"}
    return {"attendance": attendance}

@app.post("/insights/", response_model=Dict[str, str])
async def get_insights(request: InsightsRequest, db=Depends(get_db)):
    """Get AI-generated insights from attendance data"""
    return {"insights": ai_service.generate_insights(db, request.user_query)}

# Health check endpoint
@app.get("/health")
async def health_check():
    """Check API health status"""
    return {"status": "healthy", "version": app.version}

if __name__ == '__main__':
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)