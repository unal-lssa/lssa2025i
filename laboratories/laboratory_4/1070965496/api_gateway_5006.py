from flask import Flask, request, jsonify
import jwt, requests
from functools import wraps
import random

app = Flask(__name__)
SECRET_KEY = "secret"

CACHES = ["http://127.0.0.1:5004", "http://127.0.0.1:5007"]

def get_cache_instance():
    return random.choice(CACHES)

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

@app.route("/data", methods=["GET"])
@token_required
def get_data():
    cache_url = get_cache_instance()
    cache_resp = requests.get(f"{cache_url}/cache/my_data").json()
    if cache_resp['value']:
        return jsonify({'cached': True, 'data': cache_resp['value']})
    db_resp = requests.get("http://127.0.0.1:5002/db").json()
    requests.post(f"{cache_url}/cache/my_data", json={'value': db_resp['message']})
    return jsonify({'cached': False, 'data': db_resp['message']})

@app.route("/longtask", methods=["POST"])
@token_required
def long_task():
    payload = request.json
    requests.post("http://127.0.0.1:5005/task", json=payload)
    return jsonify({'status': 'Task queued'}), 202

if __name__ == "__main__":
    app.run(port=5006, debug=True)