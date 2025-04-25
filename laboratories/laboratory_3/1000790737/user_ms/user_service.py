from flask import Flask, jsonify, request
import requests

USER_DB_URL = "http://user_db:5001"

app = Flask(__name__)


@app.route("/user", methods=["POST"])
def create_user():
    data: dict | None = request.get_json()
    if not data:
        return jsonify({"error": "Invalid input"}), 400
    elif "username" not in data or "password" not in data or "role" not in data:
        return jsonify({"error": "Missing required fields"}), 400
    elif data["role"] not in ["admin", "user"]:
        return jsonify({"error": "Invalid role"}), 400

    # Simulate user creation
    body = {
        "username": data["username"],
        "password": data["password"],
        "role": data["role"],
    }
    response = requests.post(USER_DB_URL + "/users", json=body)
    if response.status_code != 201:
        return (
            jsonify({"error": response.json().get("message", "Error creating user")}),
            500,
        )

    return jsonify({"message": "User created", "user": data}), 201


@app.route("/user/<username>", methods=["GET"])
def get_user(username: str):
    response = requests.get(USER_DB_URL + f"/users/{username}")
    if response.status_code != 200:
        return (
            jsonify({"error": response.json().get("message", "User not found")}),
            404,
        )
    return jsonify(response.json()), 200


@app.route("/user/<username>/role", methods=["PUT"])
def update_user_role(username: str):
    data: dict | None = request.get_json()
    if not data or "role" not in data:
        return jsonify({"error": "Invalid input"}), 400
    elif data["role"] not in ["admin", "user"]:
        return jsonify({"error": "Invalid role"}), 400

    response = requests.put(USER_DB_URL + f"/users/{username}/role", json=data)
    if response.status_code != 200:
        return (
            jsonify({"error": response.json().get("message", "Error updating role")}),
            500,
        )

    return jsonify({"message": "User role updated", "user": data}), 200


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
