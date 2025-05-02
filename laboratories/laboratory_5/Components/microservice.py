from flask import Flask, jsonify
import requests
import os
import time
import threading
from functools import wraps
from Components.status_tracker import register_status

SERVICE_NAME = "MICROSERVICE"
app = Flask(__name__)

# Variables compartidas para rate limiting
request_timestamps = []
rate_lock = threading.Lock()

# Decorador para aplicar rate limiting
def rate_limited(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        global request_timestamps

        MAX_REQUESTS = int(os.getenv("MAX_REQUESTS_PER_TIME", 2))
        RATE_TIME = int(os.getenv("RATE_LIMIT_TIME", 60))
        now = time.time()
        with rate_lock:
            # Eliminar timestamps antiguos
            request_timestamps[:] = [t for t in request_timestamps if now - t < RATE_TIME]
            if len(request_timestamps) >= MAX_REQUESTS:
                print("Microservice error': 'Too many requests, try again later")
                register_status(SERVICE_NAME, 429)
                return jsonify({'Microservice error': 'Too many requests, try again later'}), 429
            request_timestamps.append(now)

        return f(*args, **kwargs)
    return decorated_function

@app.route("/process", methods=["GET"])
@rate_limited
def process():
    return jsonify({'message': 'Business logic executed'}), 200


@app.route("/data", methods=["GET"])
@rate_limited
def get_data():
    try:
        cache_resp = requests.get("http://127.0.0.1:5004/cache/my_data").json()
        if cache_resp['value']:
            register_status(SERVICE_NAME, 200)
            return jsonify({'cached': True, 'data': cache_resp['value']}), 200

        db_resp = requests.get("http://127.0.0.1:5002/db").json()
        requests.post("http://127.0.0.1:5004/cache/my_data", json={'value': db_resp['message']})
        return jsonify({'cached': False, 'data': db_resp['message']})
    except Exception as e:
        register_status(SERVICE_NAME, 500)
        return jsonify({'error': 'Failed to retrieve data', 'details': str(e)}), 500

if __name__ == "__main__":
    app.run(port=5001, debug=True)
