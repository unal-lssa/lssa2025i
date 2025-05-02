import itertools
from functools import wraps
from flask import Flask, jsonify, redirect
import time
import threading
import os
from Components.status_tracker import register_status

SERVICE_NAME = "LOADBALANCER_MS"
app = Flask(__name__)
microservices = itertools.cycle(["http://127.0.0.1:5001", "http://127.0.0.1:5006"])

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
                print("Load Balancer MS: 'Too many requests, try again later'")
                register_status(SERVICE_NAME, 429)
                return jsonify({'Load Balancer MS': 'Too many login attempts, try again later'}), 429
            request_timestamps.append(now)

        return f(*args, **kwargs)
    return decorated_function

@app.route("/<path:path>", methods=["GET", "POST"])
@rate_limited
def forward(path):
    target = next(microservices)
    return redirect(f"{target}/{path}", code=307)

if __name__ == "__main__":
    app.run(port=8001, debug=True)