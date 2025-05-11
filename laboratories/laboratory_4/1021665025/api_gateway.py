from flask import Flask, request, jsonify
import jwt, requests
from functools import wraps
from threading import Thread
import time

app = Flask(__name__)
SECRET_KEY = "secret"

# Decorators (reuse token auth if desired)
def token_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token: return jsonify({'error': 'Missing token'}), 403
        try: jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except: return jsonify({'error': 'Invalid token'}), 403
        return f(*args, **kwargs)
    return wrapper

# Cached data access
@app.route("/data", methods=["GET"])
@token_required
def get_data():
    cache_resp = requests.get("http://127.0.0.1:5004/cache/my_data").json()
    if cache_resp['value']:
        return jsonify({'cached': True, 'data': cache_resp['value']})
    # Simulate DB fetch
    db_resp = requests.get("http://127.0.0.1:5002/db").json()
    requests.post("http://127.0.0.1:5004/cache/my_data", json={'value': db_resp['message']})
    return jsonify({'cached': False, 'data': db_resp['message']})

# Trigger async task
@app.route("/longtask", methods=["POST"])
@token_required
def long_task():
    payload = request.json
    requests.post("http://127.0.0.1:5005/task", json=payload)
    return jsonify({'status': 'Task queued'}), 202

if __name__ == "__main__":
    app.run(port=5000, debug=True)