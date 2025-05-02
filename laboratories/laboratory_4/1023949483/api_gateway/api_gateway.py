from flask import Flask, request, jsonify
import jwt, requests
from functools import wraps
import socket  # for logging which gateway handled the request

app = Flask(__name__)
SECRET_KEY = "secret"

# Optional authentication decorator
def token_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({'error': 'Missing token'}), 403
        try:
            jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except:
            return jsonify({'error': 'Invalid token'}), 403
        return f(*args, **kwargs)
    return wrapper

# GET /data: Try cache first, then fallback to DB
@app.route("/data", methods=["GET"])
# @token_required
def get_data():
    # Try reading from cache
    cache_resp = requests.get("http://cache_service:5004/cache/my_data").json()
    if cache_resp['value']:
        return jsonify({'cached': True, 'data': cache_resp['value']})

    # If not cached, fetch from database
    db_resp = requests.get("http://database_service:5002/db").json()

    # Save in cache (no TTL)
    requests.post("http://cache_service:5004/cache/my_data", json={
        'value': db_resp['message']
    })

    return jsonify({'cached': False, 'data': db_resp['message']})

# POST /longtask: Queue an async task
@app.route("/longtask", methods=["POST"])
# @token_required
def long_task():
    payload = request.json
    requests.post("http://worker_service:5005/task", json=payload)
    return jsonify({'status': 'Task queued'}), 202

# Start the service
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
