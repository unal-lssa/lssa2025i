from flask import Flask, jsonify, request
import logging
from datetime import datetime

app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='order_service.log'
)
logger = logging.getLogger(__name__)

# Mock orders database
orders = {
    "ord1001": {"id": "ord1001", "user_id": "u1001", "product_id": "p1001", "amount": 250.00, "status": "completed", "date": "2025-04-01"},
    "ord1002": {"id": "ord1002", "user_id": "u1001", "product_id": "p1002", "amount": 120.50, "status": "processing", "date": "2025-04-15"},
    "ord1003": {"id": "ord1003", "user_id": "an1001", "product_id": "p1001", "amount": 250.00, "status": "completed", "date": "2025-04-10"}
}

@app.route('/order', methods=['GET'])
def get_orders():
    logger.info("Request received for all orders")
    return jsonify({"orders": list(orders.values())}), 200


if __name__ == "__main__":
    logger.info("Order Service starting up...")
    app.run(debug=True, host='0.0.0.0', port=5004)