from flask import Flask, request, jsonify
import requests
from functools import wraps
from Components.status_tracker import register_status
app = Flask(__name__)
SECRET_KEY = "secret"
SERVICE_NAME = "APIGATEWAY"
USERS = {
    "user1": "password123"
}


def token_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({'error': 'Missing or invalid token 11'}), 403

        token = auth_header.split(" ")[1]
        response = requests.post("http://127.0.0.1:5009/validate_token", json={"token": token})

        if response.status_code != 200:
            return jsonify({'error': 'Invalid or expired token'}), 403

        return f(*args, **kwargs)

    return wrapper


# Cached data access
@app.route("/data", methods=["GET"])
@token_required
def get_data():
    response = requests.get("http://127.0.0.1:8001/data")
    register_status(SERVICE_NAME, response.status_code)
    return jsonify(response.json()), response.status_code

# Trigger async task
@app.route("/longtask", methods=["POST"])
@token_required
def long_task():
    payload = request.json
    requests.post("http://127.0.0.1:5005/task", json=payload)
    register_status(SERVICE_NAME, 202)
    return jsonify({'status': 'Task queued'}), 202


# Route for user login (returns JWT token)
@app.route('/login', methods=['POST'])
def login():
    payload = request.json
    response = requests.post("http://127.0.0.1:5009/login", json=payload)
    register_status(SERVICE_NAME, response.status_code)
    return jsonify(response.json()), response.status_code


if __name__ == "__main__":
    app.run(port=5000, debug=True)