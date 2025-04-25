from flask import Flask, jsonify, request

# Mock map within users and monetary data
USERS_DATA_MAP: dict[str, float] = {
    "user1": 1201.0,
    "user2": 2000.0,
    "user3": 3000.0,
}

app = Flask(__name__)


@app.route("/connect", methods=["GET"])
def db_access():
    """Simulate valid database access"""
    return jsonify({"message": "Database access granted"}), 200


@app.route("/data/user", methods=["GET"])
def get_user_data():
    """Get user data"""
    username: str | None = request.args.get("username")
    if username and username in USERS_DATA_MAP:
        return jsonify({"username": username, "balance": USERS_DATA_MAP[username]}), 200
    else:
        return jsonify({"message": "User not found"}), 404


@app.route("/data/user", methods=["PUT"])
def update_user_data():
    """Update user data"""
    username: str | None = request.args.get("username")
    amount: float | None = request.json.get("amount")
    if not username or not amount:
        return jsonify({"message": "Username and amount are required"}), 400

    if username in USERS_DATA_MAP:
        USERS_DATA_MAP[username] += amount
        return (
            jsonify(
                {
                    "message": f"User {username} balance updated to {USERS_DATA_MAP[username]}"
                }
            ),
            200,
        )
    else:
        USERS_DATA_MAP[username] = amount
        return (
            jsonify({"message": f"User {username} created with balance {amount}"}),
            201,
        )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
