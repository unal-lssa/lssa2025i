from flask import Flask, jsonify, request
import socket
from functools import wraps

try: 
    AUTHORIZED_IP = socket.gethostbyname('products-microservice')
except socket.gaierror:
    AUTHORIZED_IP = None
    print("Error: Unable to resolve 'products-microservice' to an IP address")

PRODUCTS = {
    "Playstation 5": 499.99,
    "Xbox Series X": 499.99,
    "Nintendo Switch": 299.99,
    "Gaming PC": 1200.00,
}

app = Flask(__name__)

def limit_exposure(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_ip = request.remote_addr
        if client_ip != AUTHORIZED_IP:  
            return jsonify({'message': 'Forbidden: Unauthorized IP'}), 403
        return f(*args, **kwargs)
    return decorated_function


@app.route('/products', methods=['GET'])
@limit_exposure
def product_db():
    try:
        if not PRODUCTS:
            return jsonify({'message': 'No products available'}), 404
        products_formatted = {k: str(v) for k, v in PRODUCTS.items()}
        return jsonify(products_formatted), 200 
    except Exception as e:
        return jsonify({'message': 'Error at products-database', 'Details: ': str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=5004)