from functools import wraps
from flask import Flask, jsonify
import time
import threading
import os
from Components.status_tracker import register_status

SERVICE_NAME = "DATABASE"
app = Flask(__name__)
request_timestamps = []
rate_lock = threading.Lock()

# Decorador para rate limiting
def rate_limited(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        global request_timestamps

        MAX_REQUESTS = int(os.getenv("MAX_REQUESTS_PER_TIME", 2))
        RATE_TIME = int(os.getenv("RATE_LIMIT_TIME", 60))

        now = time.time()
        with rate_lock:
            request_timestamps[:] = [t for t in request_timestamps if now - t < RATE_TIME]
            if len(request_timestamps) >= MAX_REQUESTS:
                print("Database error: 'Too many requests, try again later'")
                register_status(SERVICE_NAME, 429)
                return jsonify({'Database Error': 'Too many login attempts, try again later'}), 429
            request_timestamps.append(now)

        return f(*args, **kwargs)
    return decorated_function
@app.route("/db", methods=["GET"])
@rate_limited
def db_data():
    register_status(SERVICE_NAME, 200)
    return jsonify({'message': 'Fetched fresh data from DB'})

if __name__ == "__main__":
    app.run(port=5002, debug=True)
