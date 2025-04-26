from flask import Flask, request, jsonify
import jwt
import os
import bcrypt
from datetime import datetime, timedelta
from functools import wraps

app = Flask(__name__)

SECRET_KEY = os.environ.get('SECRET_KEY', "your_secret_key")
API_KEY = os.environ.get('AUTH_SERVICE_KEY', 'auth_secret_key')

# Mock user database with hashed passwords
USERS = {
    "admin": {
        "password": bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
        "role": "ADMIN",
        "id": "1"
    },
    "user1": {
        "password": bcrypt.hashpw("password123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
        "role": "USER",
        "id": "2"
    }
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

@app.route('/login', methods=['POST'])
@require_api_key
def login():
    if not request.is_json:
        return jsonify({'message': 'Missing JSON data'}), 400
        
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'message': 'Missing username or password'}), 400
    
    if username not in USERS:
        return jsonify({'message': 'Invalid credentials'}), 401
        
    # Check password using bcrypt
    if not bcrypt.checkpw(password.encode('utf-8'), USERS[username]["password"].encode('utf-8')):
        return jsonify({'message': 'Invalid credentials'}), 401
    
    # Generate JWT token with expiration, role and additional claims
    expiration = datetime.utcnow() + timedelta(hours=1)
    token = jwt.encode({
        'sub': USERS[username]["id"],
        'username': username,
        'role': USERS[username]["role"],
        'exp': expiration,
        'iat': datetime.utcnow()
    }, SECRET_KEY, algorithm="HS256")
    
    # Generate refresh token with longer expiration
    refresh_expiration = datetime.utcnow() + timedelta(days=7)
    refresh_token = jwt.encode({
        'sub': USERS[username]["id"],
        'type': 'refresh',
        'exp': refresh_expiration,
        'iat': datetime.utcnow()
    }, SECRET_KEY, algorithm="HS256")
    
    return jsonify({
        'token': token,
        'refresh_token': refresh_token,
        'expires_in': 3600,  # 1 hour in seconds
        'token_type': 'Bearer',
        'user_id': USERS[username]["id"],
        'role': USERS[username]["role"]
    })

@app.route('/refresh', methods=['POST'])
@require_api_key
def refresh_token():
    if not request.is_json:
        return jsonify({'message': 'Missing JSON data'}), 400
        
    data = request.get_json()
    refresh_token = data.get('refresh_token')
    
    if not refresh_token:
        return jsonify({'message': 'Missing refresh token'}), 400
    
    try:
        # Validate the refresh token
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=["HS256"])
        
        # Check if it's actually a refresh token
        if payload.get('type') != 'refresh':
            return jsonify({'message': 'Invalid token type'}), 401
            
        user_id = payload.get('sub')
        
        # Find the user by ID
        user = None
        username = None
        for uname, data in USERS.items():
            if data['id'] == user_id:
                user = data
                username = uname
                break
                
        if not user:
            return jsonify({'message': 'User not found'}), 401
            
        # Generate new access token
        expiration = datetime.utcnow() + timedelta(hours=1)
        token = jwt.encode({
            'sub': user_id,
            'username': username,
            'role': user['role'],
            'exp': expiration,
            'iat': datetime.utcnow()
        }, SECRET_KEY, algorithm="HS256")
        
        return jsonify({
            'token': token,
            'expires_in': 3600,  # 1 hour in seconds
            'token_type': 'Bearer'
        })
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Refresh token expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Invalid refresh token'}), 401

@app.route('/validate', methods=['POST'])
@require_api_key
def validate_token():
    if not request.is_json:
        return jsonify({'message': 'Missing JSON data'}), 400
        
    data = request.get_json()
    token = data.get('token')
    
    if not token:
        return jsonify({'message': 'Missing token'}), 400
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return jsonify({'valid': True, 'user': payload})
    except jwt.ExpiredSignatureError:
        return jsonify({'valid': False, 'message': 'Token expired'})
    except jwt.InvalidTokenError:
        return jsonify({'valid': False, 'message': 'Invalid token'})

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001)
