# app.py
import os
import psycopg2
from psycopg2.extras import RealDictCursor # To get results as dictionaries
from flask import Flask, jsonify, request
import time

app = Flask(__name__)

def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    conn = None
    retries = 5
    while retries > 0:
        try:
            conn = psycopg2.connect(
                host=os.environ.get('DB_HOST'),
                database=os.environ.get('DB_NAME'),
                user=os.environ.get('DB_USER'),
                password=os.environ.get('DB_PASS'),
                port=os.environ.get('DB_PORT', 5432) # Default port if not set
            )
            print("Database connection successful!")
            return conn
        except psycopg2.OperationalError as e:
            print(f"Database connection failed: {e}")
            retries -= 1
            if retries == 0:
                print("Giving up on database connection.")
                raise # Reraise the exception if retries are exhausted
            print(f"Retrying database connection in 5 seconds... ({retries} retries left)")
            time.sleep(5)
    return None # Should not be reached if raise is hit

@app.route('/')
def index():
    """Basic index route."""
    return jsonify({"message": "Welcome to the Agenda API!"})

@app.route('/meetings', methods=['GET'])
def get_meetings():
    """Fetches all meetings from the meetings table."""
    conn = None # Initialize conn to None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Could not connect to the database"}), 500

        # Use RealDictCursor to get results as dictionaries
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute('SELECT meeting_id, title, start_time, end_time, location, description, created_at FROM meetings ORDER BY start_time;')
            meetings = cur.fetchall()

        return jsonify(meetings)

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        # Consider more specific error handling/logging
        return jsonify({"error": "Database query failed", "details": str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({"error": "An internal server error occurred", "details": str(e)}), 500
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) # debug=True for development convenience