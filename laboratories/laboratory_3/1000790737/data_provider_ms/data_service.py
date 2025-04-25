from flask import Flask, jsonify, request
import requests

USER_DB_URL = "http://data_db:5001"

app = Flask(__name__)


@app.route("/data/user", methods=["GET"])
def get_user_data():
    """Get user data"""
    username: str | None = request.args.get("username")
    if username:
        response = requests.get(
            USER_DB_URL + "/data/user", params={"username": username}
        )
        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            return jsonify({"message": "User not found"}), 404
    else:
        return jsonify({"message": "Username is required"}), 400


@app.route("/data/user", methods=["PUT"])
def update_user_data():
    """Update user data"""
    username: str | None = request.args.get("username")
    amount: float | None = request.json.get("amount")
    if not username or not amount:
        return jsonify({"message": "Username and amount are required"}), 400
    response = requests.put(
        USER_DB_URL + "/data/user",
        params={"username": username},
        json={"amount": amount},
    )
    if response.status_code == 200:
        return (
            jsonify(
                {
                    "message": f"User {username} balance updated to {response.json()['balance']}"
                }
            ),
            200,
        )
    elif response.status_code == 201:
        return (
            jsonify(
                {
                    "message": f"User {username} created with balance {response.json()['balance']}"
                }
            ),
            201,
        )
    else:
        return jsonify({"message": "Failed to update user data"}), 500


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
