from flask import Flask, jsonify, request

# Mock roles for the sake of the example
ROLES: dict[str, str] = {
    "ADMIN": "admin",
    "USER": "user",
    "GUEST": "guest",
}

# Mock users for the sake of the example
USERS: dict[str, dict[str]] = {
    "user1": {
        "password": "password123",
        "role": ROLES["ADMIN"],
    },
    "user2": {
        "password": "password456",
        "role": ROLES["USER"],
    },
    "guest1": {
        "password": "guestpass",
        "role": ROLES["GUEST"],
    },
}

app = Flask(__name__)


@app.route("/connect", methods=["GET"])
def db_access():
    """Simulate valid database access"""
    return jsonify({"message": "Database access granted"}), 200


@app.route("/users", methods=["POST"])
def create_user():
    """Create a new user"""
    data: dict | None = request.get_json()
    username: str | None = data.get("username")
    password: str | None = data.get("password")
    role: str | None = data.get("role")

    if not data or not username or not password or not role:
        return jsonify({"error": "Invalid input"}), 400

    if username in USERS:
        return jsonify({"message": "User already exists"}), 400

    if role not in ROLES.values():
        return jsonify({"message": "Invalid role"}), 400

    USERS[username] = {"password": password, "role": role}
    return jsonify({"message": "User created", "user": data}), 201


@app.route("/users/<username>", methods=["GET"])
def get_user(username: str):
    """Select a specific user"""
    if username in USERS:
        return jsonify({"user": username, "role": USERS[username]["role"]}), 200
    else:
        return jsonify({"message": "User not found"}), 404


@app.route("/users/<username>/role", methods=["PUT"])
def update_user_role(username: str):
    """Update a user's role"""
    if username in USERS:
        new_role: str | None = request.json.get("role")
        if new_role and new_role in ROLES.values():
            USERS[username]["role"] = new_role
            return (
                jsonify({"message": f"User {username} role updated to {new_role}"}),
                200,
            )
        else:
            return jsonify({"message": "Invalid role"}), 400
    else:
        return jsonify({"message": "User not found"}), 404


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
