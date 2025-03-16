import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables from .env file
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')  # Adjust the path if needed
load_dotenv(dotenv_path)

def get_connection():
    """
    Establishes and returns a connection to the PostgreSQL database.
    Database: Event_Management
    """
    try:
        # Fetch credentials from .env
        db_host = os.getenv("DB_HOST")
        db_name = os.getenv("DB_NAME")
        db_user = os.getenv("DB_USER")
        db_pass = os.getenv("DB_PASS")

        if not all([db_host, db_name, db_user, db_pass]):
            raise EnvironmentError("Some database credentials are missing from the .env file.")

        conn = psycopg2.connect(
            host=db_host,
            database=db_name,
            user=db_user,
            password=db_pass
        )
        print("Successfully connected to the database.")
        return conn
    except Exception as e:
        print("Error connecting to PostgreSQL database:", e)
        raise e

if __name__ == "__main__":
    # Test the connection by calling get_connection()
    try:
        conn = get_connection()
        conn.close()
    except Exception as e:
        print("Database connection test failed:", e)
