from flask import Flask, request, jsonify
import jwt
import os
import requests
from functools import wraps

app = Flask(__name__)

# Configuration
SECRET_KEY = os.environ.get('SECRET_KEY', "your_secret_key")
API_KEY = os.environ.get('PRODUCT_SERVICE_KEY', 'product_secret_key')
AUTH_SERVICE_URL = os.environ.get('AUTH_SERVICE_URL', 'http://localhost:5001')
AUTH_SERVICE_API_KEY = os.environ.get('AUTH_SERVICE_KEY', 'auth_secret_key')

# Mock product database
PRODUCTS = {
    "1": {"id": "1", "name": "Laptop", "price": 999.99, "description": "High-end laptop"},
    "2": {"id": "2", "name": "Smartphone", "price": 499.99, "description": "Latest smartphone"},
    "3": {"id": "3", "name": "Headphones", "price": 99.99, "description": "Noise-cancelling headphones"}
}

# API key validation decorator
def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        provided_key = request.headers.get('X-API-Key')
        if provided_key != API_KEY:
            return jsonify({'message': 'Invalid API key'}), 403
        return f(*args, **kwargs)
    return decorated_function

# Token validation decorator
def require_auth_token(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'message': 'Missing authentication token'}), 401
            
        # Remove Bearer prefix if present
        if token.startswith('Bearer '):
            token = token[7:]
            
        # Validate token with auth service
        try:
            response = requests.post(
                f"{AUTH_SERVICE_URL}/validate",
                json={'token': token},
                headers={'X-API-Key': AUTH_SERVICE_API_KEY}
            )
            
            if response.status_code != 200:
                return jsonify({'message': 'Invalid token'}), 401
                
            validation_result = response.json()
            if not validation_result.get('valid', False):
                return jsonify({'message': validation_result.get('message', 'Invalid token')}), 401
                
            # Store user info in request
            request.user = validation_result.get('user')
        except Exception as e:
            return jsonify({'message': f'Authentication error: {str(e)}'}), 500
            
        return f(*args, **kwargs)
    return decorated_function

# Access control decorator
def require_role(allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(request, 'user'):
                return jsonify({'message': 'User not authenticated'}), 401
                
            user_role = request.user.get('role')
            if user_role not in allowed_roles:
                return jsonify({'message': 'Insufficient permissions'}), 403
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route('/products', methods=['GET'])
@require_api_key
@require_auth_token
@require_role(['ADMIN', 'USER'])
def get_products():
    return jsonify(list(PRODUCTS.values())), 200

@app.route('/products/<product_id>', methods=['GET'])
@require_api_key
@require_auth_token
@require_role(['ADMIN', 'USER'])
def get_product(product_id):
    if product_id not in PRODUCTS:
        return jsonify({'message': 'Product not found'}), 404
        
    return jsonify(PRODUCTS[product_id]), 200

@app.route('/products', methods=['POST'])
@require_api_key
@require_auth_token
@require_role(['ADMIN'])
def create_product():
    if not request.is_json:
        return jsonify({'message': 'Missing JSON data'}), 400
        
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['name', 'price']
    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'Missing required field: {field}'}), 400
            
    # Create new product
    new_id = str(len(PRODUCTS) + 1)
    PRODUCTS[new_id] = {
        "id": new_id,
        "name": data['name'],
        "price": data['price'],
        "description": data.get('description', '')
    }
    
    return jsonify(PRODUCTS[new_id]), 201

@app.route('/products/<product_id>', methods=['PUT'])
@require_api_key
@require_auth_token
@require_role(['ADMIN'])
def update_product(product_id):
    if product_id not in PRODUCTS:
        return jsonify({'message': 'Product not found'}), 404
        
    if not request.is_json:
        return jsonify({'message': 'Missing JSON data'}), 400
        
    data = request.get_json()
    
    # Update product fields
    for field in ['name', 'price', 'description']:
        if field in data:
            PRODUCTS[product_id][field] = data[field]
            
    return jsonify(PRODUCTS[product_id]), 200

@app.route('/products/<product_id>', methods=['DELETE'])
@require_api_key
@require_auth_token
@require_role(['ADMIN'])
def delete_product(product_id):
    if product_id not in PRODUCTS:
        return jsonify({'message': 'Product not found'}), 404
        
    del PRODUCTS[product_id]
    return jsonify({'message': 'Product deleted successfully'}), 200

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5003)
