from flask import Flask, jsonify, request
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='product_service.log'
)
logger = logging.getLogger(__name__)

# Mock products database
products = {
    "p1001": {"id": "p1001", "name": "Laptop Pro", "price": 1250.00, "stock": 25},
    "p1002": {"id": "p1002", "name": "Smartphone X", "price": 850.50, "stock": 42},
    "p1003": {"id": "p1003", "name": "Wireless Headphones", "price": 120.00, "stock": 78}
}

@app.route('/product', methods=['GET'])
def get_products():
    logger.info("Request received for all products")
    return jsonify({"products": list(products.values())}), 200


if __name__ == "__main__":
    logger.info("Product Service starting up...")
    app.run(debug=True, host='0.0.0.0', port=5005)