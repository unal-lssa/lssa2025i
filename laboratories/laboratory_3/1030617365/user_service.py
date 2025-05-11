from flask import Flask, jsonify, request
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='user_service.log'
)
logger = logging.getLogger(__name__)

# Mock user database
users = {
    "user1": {"id": "u1001", "name": "John Doe", "email": "john@example.com"},
    "admin1": {"id": "a1001", "name": "Admin User", "email": "admin@example.com"},
    "analyst1": {"id": "an1001", "name": "Data Analyst", "email": "analyst@example.com"}
}

@app.route('/user', methods=['GET'])
def get_users():
    logger.info("Request received for all users")
    return jsonify({"users": list(users.values())}), 200


if __name__ == "__main__":
    logger.info("User Service starting up...")
    app.run(debug=True, host='0.0.0.0', port=5003)