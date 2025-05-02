from flask import Flask, request, jsonify
from functools import wraps
import requests
import jwt

app = Flask(__name__)
SECRET_KEY = "secret"

# Mock users for the sake of the example
USERS = {"user1": "password123"}


# Function to check JWT token
def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"message": "Token is missing!"}), 403
        try:
            jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except:
            return jsonify({"message": "Token is invalid!"}), 403
        return f(*args, **kwargs)

    return decorated_function


# Route for user login (returns JWT token)
@app.route("/login", methods=["POST"])
def login():
    auth = request.get_json()
    username = auth.get("username")
    password = auth.get("password")
    if USERS.get(username) == password:
        token = jwt.encode({"username": username}, SECRET_KEY, algorithm="HS256")
        return jsonify({"token": token})
    return jsonify({"message": "Invalid credentials"}), 401


# Cached data access
@app.route("/data", methods=["GET"])
@token_required
def get_data():
    cache_resp = requests.get("http://cache:5000/cache/my_data").json()
    if cache_resp["value"]:
        return jsonify({"cached": True, "data": cache_resp["value"]})
    # Simulate DB fetch
    db_resp = requests.get("http://database:5000/db").json()
    requests.post("http://cache:5000/cache/my_data", json={"value": db_resp["message"]})
    return jsonify({"cached": False, "data": db_resp["message"]})


# Trigger async task
@app.route("/longtask", methods=["POST"])
@token_required
def long_task():
    payload = request.json
    requests.post("http://worker:5000/task", json=payload)
    return jsonify({"status": "Task queued"}), 202


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
