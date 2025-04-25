from flask import Flask, jsonify, request

# Mock database for the sake of the example
# user1 : [{"transaction_id": 1, "amount": 100.0, dest: "user2"}, ...]
TRANSACTIONS_MAP: dict[str, list[dict]] = {
    "user1": [
        {"transaction_id": 1, "amount": 100.0, "dest": "user2"},
        {"transaction_id": 2, "amount": 50.0, "dest": "user3"},
    ],
    "user2": [
        {"transaction_id": 3, "amount": 200.0, "dest": "user1"},
    ],
}

app = Flask(__name__)


@app.route("/connect", methods=["GET"])
def db_access():
    """Simulate valid database access"""
    return jsonify({"message": "Database access granted"}), 200


@app.route("/transactions/user/<username>", methods=["GET"])
def get_user_transactions(username: str):
    """Get transactions for a user"""
    if username in TRANSACTIONS_MAP:
        return (
            jsonify({"username": username, "transactions": TRANSACTIONS_MAP[username]}),
            200,
        )
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

    if username not in TRANSACTIONS_MAP:
        TRANSACTIONS_MAP[username] = []
    TRANSACTIONS_MAP[username].append(transaction)

    return jsonify({"message": "Transaction added"}), 200


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
