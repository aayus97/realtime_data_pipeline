import psycopg2
from psycopg2 import OperationalError
from db.config import DB_CONFIG
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def connect_to_db():
    """
    Connects to the PostgreSQL database using DB_CONFIG.
    """
    try:
        return psycopg2.connect(**DB_CONFIG)
    except Exception as e:
        logger.error(f"Failed to connect to the database: {e}")
        raise

@retry(
    stop=stop_after_attempt(5),  # Retry up to 5 times
    wait=wait_exponential(multiplier=1, min=2, max=10),  # Exponential backoff
    retry=retry_if_exception_type(OperationalError),  # Retry only on OperationalError
)
def execute_query(query, data=None):
    """
    Executes a SQL query with retries on transient failures.
    :param query: The SQL query to execute.
    :param data: Data to use for parameterized query execution (optional).
    """
    conn = None
    cur = None
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        if data:
            logger.debug(f"Executing query: {query} with data: {data[:1]}... (and more)")
            cur.executemany(query, data)
        else:
            logger.debug(f"Executing query: {query}")
            cur.execute(query)
        conn.commit()
        logger.info("Query executed successfully.")
    except OperationalError as oe:
        logger.warning(f"OperationalError occurred: {oe}. Retrying...")
        raise  # Trigger retry for OperationalError
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Query execution error: {e}")
        raise
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
