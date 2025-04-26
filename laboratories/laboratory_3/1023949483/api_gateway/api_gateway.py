from datetime import datetime, timedelta
from flask import Flask, g, request, jsonify
import jwt
from functools import wraps
from mock_data import USERS
import requests

app = Flask(__name__)
SECRET_KEY = "your_secret_key"
AUTHORIZED_IPS = ["127.0.0.1", "172.19.0.1"]

# Decorators
def limit_exposure(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_ip = request.remote_addr
        if client_ip not in AUTHORIZED_IPS:
            return jsonify({'message': 'Forbidden: Unauthorized IP: ' + client_ip}), 403
        return f(*args, **kwargs)
    return decorated_function

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token_header = request.headers.get('Authorization')
        if not token_header:
            return jsonify({'message': 'Token is missing!'}), 403
        
        try:
            # Remove "Bearer " part
            token = token_header.split(" ")[1]
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            g.user = data  # Save user info globally
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token!'}), 401
        
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user.get("role") != "admin":
            return jsonify({'message': 'Admin privileges required!'}), 403
        return f(*args, **kwargs)
    return decorated_function

# Public routes
@app.route('/login', methods=['POST'])
def login():
    auth = request.get_json()
    username = auth.get('username')
    password = auth.get('password')
    user = USERS.get(username)

    if user and user['password'] == password:
        expiration = datetime.utcnow() + timedelta(minutes=30)
        token = jwt.encode(
            {
                'username': username,
                'role': user['role'],
                'exp': expiration
            },
            SECRET_KEY,
            algorithm="HS256"
        )
        return jsonify({'token': token})
    
    return jsonify({'message': 'Invalid credentials'}), 401

# Generates an expired token for testing purposes
@app.route('/expired-token', methods=['POST'])
def generate_expired_token():
    auth = request.get_json()
    username = auth.get('username')
    password = auth.get('password')
    user = USERS.get(username)

    if user and user['password'] == password:
        expired_time = datetime.utcnow() - timedelta(minutes=1)  # Token already expired
        token = jwt.encode(
            {
                'username': username,
                'role': user['role'],
                'exp': expired_time
            },
            SECRET_KEY,
            algorithm="HS256"
        )
        return jsonify({'expired_token': token})
    
    return jsonify({'message': 'Invalid credentials'}), 401


# Protected routes
@app.route('/clients', methods=['GET'])
@token_required
@limit_exposure
def proxy_client_data():
    token = request.headers.get("Authorization")
    try:
        response = requests.get(
            "http://client:5003/clients",
            headers={"Authorization": token}
        )
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({"message": f"Error contacting client service: {str(e)}"}), 500


@app.route('/admin', methods=['GET'])
@token_required
@admin_required
@limit_exposure
def proxy_user_summary():
    token = request.headers.get("Authorization")
    try:
        response = requests.get(
            "http://admin:5004/admin/users",
            headers={"Authorization": token}
        )
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({"message": f"Error contacting admin service: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)