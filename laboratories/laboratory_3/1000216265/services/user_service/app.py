from flask import Flask, request, jsonify
import jwt
import os
import requests
from functools import wraps

app = Flask(__name__)

# Configuration
SECRET_KEY = os.environ.get('SECRET_KEY', "your_secret_key")
API_KEY = os.environ.get('USER_SERVICE_KEY', 'user_secret_key')
AUTH_SERVICE_URL = os.environ.get('AUTH_SERVICE_URL', 'http://localhost:5001')
AUTH_SERVICE_API_KEY = os.environ.get('AUTH_SERVICE_KEY', 'auth_secret_key')

# Mock database of users
USERS = {
    "1": {"id": "1", "username": "admin", "email": "admin@example.com", "role": "ADMIN"},
    "2": {"id": "2", "username": "user1", "email": "user1@example.com", "role": "USER"}
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

# Token validation decorator - validates with auth service
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

@app.route('/users', methods=['GET'])
@require_api_key
@require_auth_token
@require_role(['ADMIN', 'USER'])
def get_users():
    # If regular user, only allow them to see their own data
    if request.user.get('role') == 'USER':
        user_id = request.user.get('sub')
        if user_id in USERS:
            return jsonify([USERS[user_id]]), 200
        return jsonify([]), 200
        
    # Admins can see all users
    return jsonify(list(USERS.values())), 200

@app.route('/users/<user_id>', methods=['GET'])
@require_api_key
@require_auth_token
@require_role(['ADMIN', 'USER'])
def get_user(user_id):
    # Regular users can only access their own data
    if request.user.get('role') == 'USER' and request.user.get('sub') != user_id:
        return jsonify({'message': 'Access denied'}), 403
        
    if user_id not in USERS:
        return jsonify({'message': 'User not found'}), 404
        
    return jsonify(USERS[user_id]), 200

@app.route('/users', methods=['POST'])
@require_api_key
@require_auth_token
@require_role(['ADMIN'])
def create_user():
    if not request.is_json:
        return jsonify({'message': 'Missing JSON data'}), 400
        
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['username', 'email', 'role']
    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'Missing required field: {field}'}), 400
            
    # Check if username already exists
    for user in USERS.values():
        if user['username'] == data['username']:
            return jsonify({'message': 'Username already exists'}), 409
            
    # Create new user
    new_id = str(len(USERS) + 1)
    USERS[new_id] = {
        "id": new_id,
        "username": data['username'],
        "email": data['email'],
        "role": data['role']
    }
    
    return jsonify(USERS[new_id]), 201

@app.route('/users/<user_id>', methods=['PUT'])
@require_api_key
@require_auth_token
@require_role(['ADMIN'])
def update_user(user_id):
    if user_id not in USERS:
        return jsonify({'message': 'User not found'}), 404
        
    if not request.is_json:
        return jsonify({'message': 'Missing JSON data'}), 400
        
    data = request.get_json()
    
    # Update user fields
    for field in ['username', 'email', 'role']:
        if field in data:
            USERS[user_id][field] = data[field]
            
    return jsonify(USERS[user_id]), 200

@app.route('/users/<user_id>', methods=['DELETE'])
@require_api_key
@require_auth_token
@require_role(['ADMIN'])
def delete_user(user_id):
    if user_id not in USERS:
        return jsonify({'message': 'User not found'}), 404
        
    del USERS[user_id]
    return jsonify({'message': 'User deleted successfully'}), 200

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5002)
