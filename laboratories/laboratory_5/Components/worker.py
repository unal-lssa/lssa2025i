from flask import Flask, request, jsonify
import threading
import time
import os
from Components.status_tracker import register_status
from functools import wraps

SERVICE_NAME = "WORKER"
# Variables compartidas para rate limiting
request_timestamps = []
rate_lock = threading.Lock()
app = Flask(__name__)

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
                print("Worker Login error: 'Too many requests, try again later'")
                register_status(SERVICE_NAME, 429)
                return jsonify({'Worker Login error': 'Too many login attempts, try again later'}), 429
            request_timestamps.append(now)
        return f(*args, **kwargs)
    return decorated_function

@app.route("/task", methods=["POST"])
@rate_limited
def handle_task():
    data = request.json
    thread = threading.Thread(target=process_task, args=(data,))
    thread.start()
    register_status(SERVICE_NAME, 202)
    return jsonify({'status': 'Started'}), 202

def process_task(data):
    print(f"Processing task: {data}")
    time.sleep(5)  # Simulate delay
    print("Task complete")

if __name__ == "__main__":
    app.run(port=5005, debug=True)