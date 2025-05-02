from functools import wraps
from flask import Flask, request, jsonify
import jwt, time
import threading
import os
from Components.status_tracker import register_status

SERVICE_NAME = "CACHE"
app = Flask(__name__)
cache = {}
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
                print("Error Cache :Too many requests, exiting")
                register_status(SERVICE_NAME, 429)
                return jsonify({'Error Cache': 'Too many login attempts, try again later'}), 429
            request_timestamps.append(now)

        return f(*args, **kwargs)
    return decorated_function

@app.route("/cache/<key>", methods=["GET"])
@rate_limited
def get_cache(key):
    register_status(SERVICE_NAME, 200)
    return jsonify({'value': cache.get(key)}), 200

@app.route("/cache/<key>", methods=["POST"])
@rate_limited
def set_cache(key):
    data = request.json
    cache[key] = data.get("value")
    register_status(SERVICE_NAME, 200)
    return jsonify({'status': 'ok'}), 200

if __name__ == "__main__":
    app.run(port=5004, debug=True)