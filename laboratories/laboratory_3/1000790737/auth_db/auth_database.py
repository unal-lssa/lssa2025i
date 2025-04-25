from flask import Flask, jsonify, request

# Mock map within users and tokens
USERS_TOKEN_MAP: dict[str, set[str]] = {}

app = Flask(__name__)


@app.route("/connect", methods=["GET"])
def db_access():
    """Simulate valid database access"""
    return jsonify({"message": "Database access granted"}), 200


@app.route("/token/active/<username>", methods=["GET"])
def get_count_active_tokens(username: str):
    """Get the number of active tokens for a user"""
    if username not in USERS_TOKEN_MAP:
        return jsonify({"message": "User not found"}), 404

    active_tokens = len(USERS_TOKEN_MAP[username])
    return jsonify({"active_tokens": active_tokens}), 200


@app.route("/token/valid/<username>", methods=["POST"])
def check_token_is_valid(username: str):
    """Check if a token exists for a user"""
    token: str | None = request.json.get("token")
    if not token:
        return jsonify({"message": "Token not provided"}), 400

    if username in USERS_TOKEN_MAP and token in USERS_TOKEN_MAP[username]:
        return jsonify({"is_valid": True}), 200
    return jsonify({"is_valid": False}), 404


@app.route("/token", methods=["POST"])
def new_token():
    """Save the token generated for a user"""
    username: str | None = request.json.get("username")
    token: str | None = request.json.get("token")
    if not username or not token:
        return jsonify({"message": "Username or token not provided"}), 400

    if username not in USERS_TOKEN_MAP:
        USERS_TOKEN_MAP[username] = []
    USERS_TOKEN_MAP[username].append(token)

    return jsonify({"message": "Token saved"}), 200


@app.route("/token/delete", methods=["DELETE"])
def delete_token():
    """Delete a token for a user"""
    username: str | None = request.json.get("username")
    token: str | None = request.json.get("token")
    if not username or not token:
        return jsonify({"message": "Username or token not provided"}), 400

    if username in USERS_TOKEN_MAP and token in USERS_TOKEN_MAP[username]:
        USERS_TOKEN_MAP[username].remove(token)
        return jsonify({"message": "Token deleted"}), 200
    return jsonify({"message": "Token not found"}), 404


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
