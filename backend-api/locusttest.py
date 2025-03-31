# locustfile.py
import random
import json
from datetime import datetime, timedelta
from locust import HttpUser, task, between, tag

class AttendanceAPIUser(HttpUser):
    wait_time = between(1, 3)  # Wait between 1-3 seconds between tasks
    
    def on_start(self):
        # Initialize user-specific data
        self.employee_ids = list(range(1001, 1051))  # 50 test employees
        self.departments = ["Engineering", "Marketing", "Sales", "HR", "Finance", "Operations"]
        self.statuses = ["Present", "Absent", "WFH"]
        
        # Create a date range for the past 30 days
        self.dates = [(datetime.now() - timedelta(days=x)).strftime("%Y-%m-%d") for x in range(30)]
    
    def generate_attendance_entry(self):
        """Generate a random attendance entry"""
        return {
            "employee_id": random.choice(self.employee_ids),
            "date": random.choice(self.dates),
            "status": random.choice(self.statuses),
            "department": random.choice(self.departments)
        }
    
    @tag("health")
    @task(5)
    def check_health(self):
        """Test the health check endpoint"""
        with self.client.get("/health", name="Health Check", catch_response=True) as response:
            if response.status_code == 200:
                if response.json().get("status") == "healthy":
                    response.success()
                else:
                    response.failure("Health check returned unhealthy status")
            else:
                response.failure(f"Health check failed with status {response.status_code}")
    
    @tag("read")
    @task(30)
    def get_employee_attendance(self):
        """Test getting attendance for a specific employee"""
        employee_id = random.choice(self.employee_ids)
        with self.client.get(f"/attendance/{employee_id}", name="Get Employee Attendance", catch_response=True) as response:
            if response.status_code not in [200, 404]:  # 404 is acceptable if no records
                response.failure(f"Failed to get attendance: {response.status_code}")
            else:
                response.success()
    
    @tag("read")
    @task(20)
    def get_attendance_trends(self):
        """Test getting attendance trends"""
        with self.client.get("/attendance/trends", name="Get Attendance Trends", catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Failed to get trends: {response.status_code}")
            else:
                response.success()
    
    @tag("write")
    @task(15)
    def add_attendance(self):
        """Test adding a new attendance record"""
        entry = self.generate_attendance_entry()
        with self.client.post(
            "/attendance/",
            json=entry,
            name="Add Attendance",
            catch_response=True
        ) as response:
            if response.status_code not in [200, 409]:  # 409 is acceptable for duplicates
                response.failure(f"Failed to add attendance: {response.status_code}")
            else:
                response.success()
    
    @tag("write")
    @task(10)
    def update_attendance(self):
        """Test updating an attendance record"""
        entry = self.generate_attendance_entry()
        with self.client.put(
            "/attendance/",
            json=entry,
            name="Update Attendance",
            catch_response=True
        ) as response:
            if response.status_code not in [200, 404]:  # 404 is acceptable if not found
                response.failure(f"Failed to update attendance: {response.status_code}")
            else:
                response.success()
    
    @tag("ai")
    @task(5)
    def get_insights(self):
        """Test getting AI insights (less frequent due to potential API rate limits)"""
        queries = [
            "Who was absent most this month?",
            "Which department has the highest WFH percentage?",
            "What are the attendance trends over time?",
            "Who has perfect attendance?",
            "Compare attendance between departments"
        ]
        
        with self.client.post(
            "/insights/",
            json={"user_query": random.choice(queries)},
            name="Get AI Insights",
            catch_response=True
        ) as response:
            if response.status_code != 200:
                response.failure(f"Failed to get insights: {response.status_code}")
            else:
                if "insights" in response.json():
                    response.success()
                else:
                    response.failure("Missing insights in response")

class AdminUser(AttendanceAPIUser):
    """Simulates admin users who do more analytics tasks"""
    
    @tag("ai")
    @task(20)
    def get_detailed_insights(self):
        """Admins request more complex insights"""
        complex_queries = [
            "Generate a detailed analysis of attendance patterns by department",
            "Which employees have increasing absence trends?",
            "Predict next week's attendance based on historical patterns",
            "What's the correlation between day of week and WFH status?",
            "Identify departments with potential attendance issues"
        ]
        
        with self.client.post(
            "/insights/",
            json={"user_query": random.choice(complex_queries)},
            name="Get Complex AI Insights",
            catch_response=True
        ) as response:
            if response.status_code != 200:
                response.failure(f"Failed to get complex insights: {response.status_code}")
            else:
                response.success()
    
    @tag("read")
    @task(30)
    def get_all_trends(self):
        """Admins check overall trends more frequently"""
        with self.client.get("/attendance/trends", name="Admin Trends Analysis", catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Failed to get admin trends: {response.status_code}")
            else:
                response.success()