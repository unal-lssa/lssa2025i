from flask import Flask, jsonify, request
from functools import wraps
from datetime import datetime, timedelta
import requests
import jwt
import socket

USER_DB_URL = "http://auth_db:5001"

app = Flask(__name__)
SECRET_KEY = "your_secret_key"
TOKEN_EXPIRATION_DAYS = 1
TOTAL_TOKENS_PER_USER = 5

try:
    AUTHORIZED_IP = socket.gethostbyname("api_gateway")
except:
    raise SystemExit(
        "Could not get hostname. Please check if the api_gateway service is running."
    )


def limit_exposure(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_ip = request.remote_addr
        if client_ip != AUTHORIZED_IP:
            return jsonify({"message": "Forbidden: Unauthorized IP"}), 403
        return f(*args, **kwargs)

    return decorated_function


def generate_token(username: str, role: str):
    now = datetime.now()
    payload = {
        "username": username,
        "role": role,
        "iat": now,
        "exp": now + timedelta(days=TOKEN_EXPIRATION_DAYS),
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token


@app.route("/token/valid/<username>", methods=["GET"])
@limit_exposure
def check_token_is_valid(username: str):
    """Check if a token exists for a user"""
    token: str | None = request.json.get("token")
    if not token:
        return jsonify({"message": "Token not provided"}), 400

    response = requests.post(
        USER_DB_URL + f"/token/valid/{username}", json={"token": token}
    )
    if response.status_code == 200:
        return jsonify({"is_valid": True}), 200
    return jsonify({"is_valid": False}), 404


@app.route("/token", methods=["POST"])
@limit_exposure
def new_token():
    """Save the token generated for a user"""
    username: str | None = request.json.get("username")
    role: str | None = request.json.get("role")
    if not username or not role:
        return jsonify({"message": "Username or role not provided"}), 400

    # Check if the user has reached the limit of active tokens
    response = requests.get(USER_DB_URL + f"/token/active/{username}")
    if response.status_code == 200:
        active_tokens = response.json().get("active_tokens", 0)
        if active_tokens >= TOTAL_TOKENS_PER_USER:
            return (
                jsonify({"message": "User has reached the limit of active tokens"}),
                403,
            )
    elif response.status_code == 404:
        return jsonify({"message": "User not found"}), 404
    elif response.status_code != 200:
        return jsonify({"message": "Failed to check active tokens"}), 500

    token = generate_token(username, role)
    response = requests.post(
        USER_DB_URL + "/token", json={"username": username, "token": token}
    )
    if response.status_code == 200:
        return jsonify({"token": token}), 200
    return jsonify({"message": "Failed to save token"}), 500


@app.route("/token/invalid/<username>", methods=["DELETE"])
@limit_exposure
def delete_all_tokens(username: str):
    """Delete all tokens for a user"""
    if not username:
        return jsonify({"message": "Username not provided"}), 400

    response = requests.delete(
        USER_DB_URL + "/token/delete", json={"username": username}
    )
    if response.status_code == 200:
        return jsonify({"message": "All tokens deleted"}), 200
    return jsonify({"message": "Failed to delete tokens"}), 500


if __name__ == "__main__":
    # Simulate connection to db
    response = requests.get(USER_DB_URL + "/connect")
    if response.status_code != 200:
        print("Failed to connect to db")
        raise SystemExit(
            "Could not connect to db. Please check if the db service is running."
        )
    else:
        print("Connected to db successfully")

    app.run(debug=True, host="0.0.0.0", port=5000)
