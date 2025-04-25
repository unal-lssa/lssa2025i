from flask import Flask, jsonify, request
import requests

USER_DB_URL = "http://transaction_db:5001"

app = Flask(__name__)


@app.route("/transactions.user/<username>", methods=["GET"])
def get_user_transactions(username: str):
    """Get transactions for a user"""
    response = requests.get(USER_DB_URL + f"/transactions/user/{username}")
    if response.status_code == 200:
        return jsonify(response.json()), 200
    else:
        return jsonify({"message": "User not found"}), 404


@app.route("/transaction", methods=["POST"])
def add_user_transaction():
    """Add a transaction for a user"""
    username: str | None = request.json.get("username")
    transaction: dict | None = request.json.get("transaction")
    if not username or not transaction:
        return jsonify({"message": "Username and transaction are required"}), 400
    if (
        "transaction_id" not in transaction
        or "amount" not in transaction
        or "dest" not in transaction
    ):
        return (
            jsonify(
                {"message": "Transaction must contain transaction_id, amount, and dest"}
            ),
            400,
        )

    response = requests.post(
        USER_DB_URL + "/transaction",
        json={"username": username, "transaction": transaction},
    )

    if response.status_code == 200:
        return jsonify({"message": "Transaction added"}), 200
    else:
        return jsonify({"message": "Failed to add transaction"}), 500


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
