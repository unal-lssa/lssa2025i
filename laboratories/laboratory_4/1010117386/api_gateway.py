from flask import Flask, request, jsonify
import jwt, requests
from functools import wraps
from threading import Thread
import time
import os

app = Flask(__name__)
SECRET_KEY = "secret"

USERS = {"user1": "password123"}


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


# Decorators (reuse token auth if desired)
def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"message": "Token is missing!"}), 403
        try:
            print(token)
            # Remove "Bearer " if present
            if token.startswith("Bearer "):
                token = token[7:]

            jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except Exception as e:
            print(e)
            return jsonify({"message": "Token is invalid!"}), 403
        return f(*args, **kwargs)

    return decorated_function


# Cached data access
@app.route("/data/<element>", methods=["GET"])
@token_required
def get_data(element):
    cache_resp = requests.get("http://127.0.0.1:5004/cache/" + element).json()
    if cache_resp["value"]:
        return jsonify({"cached": True, "data": cache_resp["value"]})
    # Simulate DB fetch
    db_resp = requests.get("http://127.0.0.1:5002/db/" + element).json()
    requests.post(
        "http://127.0.0.1:5004/cache/" + element, json={"value": db_resp["message"]}
    )
    return jsonify({"cached": False, "data": db_resp["message"]})


# Trigger async task
@app.route("/longtask", methods=["POST"])
@token_required
def long_task():
    payload = request.json
    requests.post("http://127.0.0.1:5005/task", json=payload)
    return jsonify({"status": "Task queued"}), 202


# Trigger async task
@app.route("/process", methods=["GET"])
@token_required
def process():
    return requests.get("http://127.0.0.1:5008/process").json()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(port=port, debug=True)
