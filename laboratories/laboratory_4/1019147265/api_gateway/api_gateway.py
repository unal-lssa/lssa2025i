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
        print("Checking token...")
        token = request.headers.get("Authorization")
        if not token: return jsonify({'error': 'Missing token'}), 403
        try: jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except: return jsonify({'error': 'Invalid token'}), 403
        return f(*args, **kwargs)
    return wrapper

# Cached data access with authentication caching
@app.route("/data", methods=["GET"])
def get_data():
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({'error': 'Missing token'}), 403

    # Check token in auth cache
    auth_resp = requests.get(f"http://cache:5004/auth/{token}").json()
    if auth_resp.get('auth_data'):
        return jsonify({'cached': True, 'data': auth_resp['auth_data']})

    # Decode token if not cached
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        # Cache the decoded token
        requests.post(f"http://cache:5004/auth/{token}", json={'auth_data': decoded})
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token expired'}), 403
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 403

    return jsonify({'cached': False, 'data': decoded})

# Trigger async task
@app.route("/longtask", methods=["POST"])
@token_required
def long_task():
    payload = request.json
    requests.post("http://worker:5005/task", json=payload)
    return jsonify({'status': 'Task queued'}), 202

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)