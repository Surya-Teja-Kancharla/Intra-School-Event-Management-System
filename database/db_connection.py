import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_connection():
    """
    Establishes and returns a connection to the PostgreSQL database.
    Database: Event_Management
    """
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            database=os.getenv("DB_NAME", "Event_Management"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASS", "kst017")
        )
        print("Successfully connected to the database.")
        return conn
    except Exception as e:
        print("Error connecting to PostgreSQL database:", e)
        raise e

if __name__ == "__main__":
    # Test the connection by calling get_connection()
    conn = get_connection()
    conn.close()
