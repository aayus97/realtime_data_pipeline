import psycopg2
from db.config import DB_CONFIG
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type


def connect_to_db():
    """Connects to the PostgreSQL database."""
    return psycopg2.connect(**DB_CONFIG)


@retry(
    stop=stop_after_attempt(5),  # Retry up to 5 times
    wait=wait_exponential(multiplier=1, min=2, max=10),  # Exponential backoff: 2s, 4s, etc.
    retry=retry_if_exception_type(psycopg2.OperationalError),  # Retry only on OperationalError
)
def execute_query(query, data=None):
    """
    Executes a query with optional parameters and retries on transient failures.
    :param query: The SQL query to execute.
    :param data: Data to use for parameterized query execution.
    """
    conn = None
    cur = None
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        if data:
            cur.executemany(query, data)
        else:
            cur.execute(query)
        conn.commit()
    except psycopg2.OperationalError as oe:
        print(f"OperationalError occurred: {oe}. Retrying...")
        raise  # Trigger retry for OperationalError
    except Exception as e:
        if conn:
            conn.rollback()
        raise Exception(f"Query execution error: {e}")
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
