# app/database.py
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import ThreadedConnectionPool
from tenacity import retry, stop_after_attempt, wait_exponential
from contextlib import contextmanager
import logging

from app.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global connection pool
connection_pool = None

@retry(
    stop=stop_after_attempt(settings.DB_RETRY_ATTEMPTS),
    wait=wait_exponential(multiplier=1, min=settings.DB_RETRY_MIN_SECONDS, max=settings.DB_RETRY_MAX_SECONDS),
    reraise=True
)
def create_connection_pool():
    """Create a threaded connection pool for database connections"""
    global connection_pool
    try:
        if connection_pool is None:
            connection_pool = ThreadedConnectionPool(
                minconn=1,
                maxconn=10,
                dsn=settings.DATABASE_URL,
                cursor_factory=RealDictCursor
            )
            logger.info("Database connection pool created successfully")
    except Exception as e:
        logger.error(f"Failed to create database connection pool: {str(e)}")
        raise
    return connection_pool

@contextmanager
def get_db():
    """Get a database connection from the pool"""
    if connection_pool is None:
        create_connection_pool()
    
    conn = None
    try:
        conn = connection_pool.getconn()
        yield conn
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Database error: {str(e)}")
        raise
    finally:
        if conn:
            connection_pool.putconn(conn)

def initialize_db():
    """Initialize database schema"""
    with get_db() as conn:
        try:
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS attendance (
                id SERIAL PRIMARY KEY,
                employee_id INT NOT NULL,
                date DATE NOT NULL,
                status VARCHAR(10) NOT NULL CHECK (status IN ('Present', 'Absent', 'WFH')),
                department VARCHAR(50) NOT NULL
            )''')
            conn.commit()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            raise