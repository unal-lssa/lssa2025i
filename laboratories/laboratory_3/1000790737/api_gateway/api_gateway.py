from flask import Flask, request, jsonify
from functools import wraps
import jwt
import requests

app = Flask(__name__)
SECRET_KEY = "your_secret_key"

SERVICES_URL = {
    "auth_service": "http://auth_service:5000",
    "user_service": "http://user_service:5000",
    "data_service": "http://data_service:5000",
    "transaction_service": "http://transaction_service:5000",
}


# Function to check JWT token
def token_required(allowed_roles=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = None
            if "Authorization" in request.headers:
                token = request.headers["Authorization"].split(" ")[1]
            if not token:
                return jsonify({"message": "Token is missing!"}), 401

            try:
                data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
                username = data["username"]
                role = data["role"]
            except jwt.ExpiredSignatureError:
                return jsonify({"message": "Token has expired!"}), 401
            except jwt.InvalidTokenError:
                return jsonify({"message": "Invalid token!"}), 401

            if allowed_roles and role not in allowed_roles:
                return jsonify({"message": "Access denied!"}), 403

            return f(*args, **kwargs)

        return decorated_function

    return decorator


# Route for user login (returns JWT token)
@app.route("/login", methods=["POST"])
def login():
    auth = request.get_json()
    username = auth.get("username")
    password = auth.get("password")

    # Get user credentials from a mock database
    response = requests.get(SERVICES_URL["user_service"] + f"/user/{username}")
    if response.status_code == 404:
        return jsonify({"message": "User not found"}), 404
    elif response.status_code == 403:
        return jsonify({"message": "User is not authorized"}), 403
    elif response.status_code != 200:
        return jsonify({"message": "Error fetching user data"}), 500

    user_data = response.json()
    if user_data["password"] != password:
        return jsonify({"message": "Invalid credentials"}), 401

    response = requests.post(
        SERVICES_URL["auth_service"] + "/token",
        json={"username": user_data["user"], "role": user_data["role"]},
    )
    if response.status_code == 403:
        return jsonify({"message": "User has too many tokens"}), 403
    elif response.status_code != 200:
        print("RESPONSE", response)
        return jsonify({"message": "Error generating token"}), 500

    return jsonify({"token": response.json().get("token")}), 200


# Protected route
@app.route("/transactions/<username>", methods=["GET"])
@token_required(allowed_roles=["admin", "user"])
def get_transactions(username: str):
    # Simulate fetching transactions for the user
    response = requests.get(
        SERVICES_URL["transaction_service"] + f"/transactions/user/{username}"
    )
    if response.status_code != 200:
        return jsonify({"message": "Error fetching transactions"}), 500

    return jsonify(response.json()), 200


@app.route("/total/username/<username>", methods=["GET"])
@token_required(allowed_roles=["admin"])
def get_money(username: str):
    response = requests.get(
        SERVICES_URL["data_service"] + f"/data/user", params={"username": username}
    )
    if response.status_code != 200:
        return jsonify({"message": "Error fetching total money"}), 500

    return jsonify(response.json()), 200


@app.route("/user/<username>/role", methods=["PUT"])
@token_required(allowed_roles=["admin"])
def update_user_role(username: str):
    data: dict | None = request.get_json()
    if not data or "role" not in data:
        return jsonify({"error": "Invalid input"}), 400
    elif data["role"] not in ["admin", "user"]:
        return jsonify({"error": "Invalid role"}), 400

    response = requests.put(
        SERVICES_URL["user_service"] + f"/users/{username}/role", json=data
    )
    if response.status_code != 200:
        return (
            jsonify({"error": response.json().get("message", "Error updating role")}),
            500,
        )

    # Delete all existing tokens for the user
    response = requests.delete(
        SERVICES_URL["auth_service"] + f"/token/invalid/{username}"
    )

    return jsonify({"message": "User role updated", "user": data}), 200


if __name__ == "__main__":
    # Uses the host 0.0.0.0 to allow access from any IP address
    app.run(debug=True, host="0.0.0.0", port=8080)
