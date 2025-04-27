import random
from flask import Flask, request, jsonify
import jwt, requests
from functools import wraps
from threading import Thread
import time
import os

app = Flask(__name__)
SECRET_KEY = "your_secret_key"
USERS = {
    "user1": { "password": "password123", "role": "user" },
    "admin": { "password": "adminpass", "role": "admin" },
}

@app.before_request
def simulate_latency():
    delay = random.uniform(0.5, 5)
    time.sleep(delay)
    print(f"Simulated latency: {delay} seconds")

# Decorators (reuse token auth if desired)
def token_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token: return jsonify({'error': 'Missing token'}), 403
        try: jwt.decode(token.split()[1], SECRET_KEY, algorithms=["HS256"])
        except: return jsonify({'error': 'Invalid token'}), 403
        return f(*args, **kwargs)
    return wrapper

# Cached data access
@app.route("/data", methods=["GET"])
@token_required
def get_data():
    cache_resp = requests.get("http://cache:5004/cache/my_data").json()
    if cache_resp['value']:
        return jsonify({'cached': True, 'data': cache_resp['value']})
    # Simulate DB fetch
    db_resp = requests.get("http://database:5002/db").json()
    requests.post("http://cache:5004/cache/my_data", json={'value': db_resp['message']})
    return jsonify({'cached': False, 'data': db_resp['message']})

# Trigger async task
@app.route("/longtask", methods=["POST"])
@token_required
def long_task():
    payload = request.json
    requests.post("http://worker:5005/task", json=payload)
    return jsonify({'status': 'Task queued'}), 202

# Route for user login (returns a JWT token)
@app.route('/login', methods=['POST'])
def login():
    auth = request.get_json()
    username = auth.get('username')
    password = auth.get('password')
    user = USERS.get(username)
    if user and user['password'] == password:
        token = jwt.encode({
            'username': username,
            'role': user['role'],
        }, SECRET_KEY, algorithm="HS256")
        return jsonify({'token': token})
    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/health', methods=['GET'])
def get_health():
    return jsonify({'status': 'OK'}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)