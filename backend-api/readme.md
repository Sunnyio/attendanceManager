# Attendance API

A production-grade REST API for tracking and analyzing employee attendance with AI-powered insights.

## Features

- Track employee attendance (Present, Absent, Work From Home)
- View attendance by employee or department
- Get attendance trends and patterns
- AI-powered insights from attendance data (Claude, GPT-4o, or Gemini)
- Production-ready with connection pooling, error handling, and retries

## Project Structure

```
attendance-api/
├── .env                    # Environment variables
├── main.py                 # Application entry point
├── app/                    # Main application package
│   ├── __init__.py
│   ├── config.py           # Configuration settings
│   ├── database.py         # Database connection and operations
│   ├── models.py           # Pydantic models for data validation
│   ├── services/           # Business logic services
│   │   ├── __init__.py
│   │   ├── attendance_service.py  # Attendance-related operations
│   │   └── ai_service.py   # AI-powered insights generation
├── tests/                  # Test directory
├── locustfile.py           # Load testing configuration
└── requirements.txt        # Project dependencies
```

## Setup and Installation

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment: 
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Copy `.env.example` to `.env` and fill in your configuration
6. Run the application: `python main.py`

## API Endpoints

- `POST /attendance/` - Add a new attendance record
- `PUT /attendance/` - Update an existing attendance record
- `GET /attendance/{employee_id}` - Get attendance records for a specific employee
- `GET /attendance/trends` - Get attendance trends across departments and employees
- `POST /insights/` - Get AI-generated insights from attendance data
- `GET /health` - Check API health status

## Load Testing

Load testing is implemented using Locust:

1. Install Locust: `pip install locust`
2. Run load test: `locust -f locustfile.py`
3. Open the Locust web UI at http://localhost:8089
4. Configure users and spawn rate, then start the test

## Environment Variables

Required environment variables:

- `DATABASE_URL` - PostgreSQL connection string
- `ANTHROPIC_KEY` - Anthropic API key (optional if not using Claude)
- `OPENAI_KEY` - OpenAI API key (optional if not using GPT)
- `GEMINI_API_KEY` - Google Gemini API key (optional if not using Gemini)
- `DEFAULT_AI_PROVIDER` - Default AI provider (claude, openai, gemini)

## Development

### Running Tests

```bash
pytest tests/
```

### Code Quality

```bash
# Run code formatters
black .
isort .

# Run linters
flake8 .
mypy .
```

## License

[MIT License](LICENSE)