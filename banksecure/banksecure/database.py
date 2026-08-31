import os

import mysql.connector
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    """
    Opens a new connection to the MySQL database using credentials
    from environment variables (see .env.example).
    Returns a mysql.connector connection object, or None on failure.
    """
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", 3306)),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "banking_fraud_analysis"),
        )
        return connection

    except mysql.connector.Error as error:
        print("Database connection error:", error)
        return None
