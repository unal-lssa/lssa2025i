import requests
from flask import Flask, request, jsonify
import jwt
from functools import wraps
import time
from datetime import datetime

app = Flask(__name__)
SECRET_KEY = "your_secret_key"
AUTHORIZED_IP = "127.0.0.1" # Only allow local access for simplicity

# Mock users for the sake of the example
USERS = {
    "user1": {"password": "password123", "role": "admin"},
    "user2": {"password": "password123", "role": "user"}
}

# For rate limiting
request_count = {}

# Function to check if the request comes from an authorized IP address
def limit_exposure(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_ip = request.remote_addr
        if client_ip not in AUTHORIZED_IP:
            return jsonify({'message': 'Forbidden: Unauthorized IP'}), 403
        return f(*args, **kwargs)
    return decorated_function

# Function to check JWT token and user role
def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 403
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            request.user = payload
        except:
            return jsonify({'message': 'Token is invalid!'}), 403
        return f(*args, **kwargs)
    return decorated_function

# Role-based access control (RBAC)
def check_role(required_role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if request.user["role"] != required_role:
                return jsonify({'message': 'Forbidden: Insufficient permissions'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Time-based restriction (only between 1 PM and 11 PM)
def time_limit(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_time = datetime.now().hour
        if current_time < 13 or current_time >= 23:
            return jsonify({'message': 'Forbidden: Requests are only allowed between 1 PM and 11 PM'}), 403
        return f(*args, **kwargs)
    return decorated_function

# Route for user login (returns JWT token)
@app.route('/login', methods=['POST'])
def login():
    auth = request.get_json()
    username = auth.get('username')
    password = auth.get('password')
    user = USERS.get(username)
    if user and user["password"] == password:
        token = jwt.encode({'username': username, 'role': user["role"]}, SECRET_KEY, algorithm="HS256")
        return jsonify({'token': token})
    return jsonify({'message': 'Invalid credentials'}), 401

# Redirect to another microservice
def redirect_to_microservice(service_url):
    headers = {'Authorization': request.headers.get('Authorization')}
    response = requests.get(service_url, headers=headers)
    return jsonify(response.json()), response.status_code

# Protected routes
@app.route('/message', methods=['GET'])
@token_required
@limit_exposure  # Apply the limit exposure tactic to this route
@check_role("user")  # Only users can access this route
@time_limit  # Only accessible between 1 PM and 11 PM
def message_service():
    return redirect_to_microservice("http://127.0.0.1:5003/message")

@app.route('/stats', methods=['GET'])
@token_required
@limit_exposure  # Apply the limit exposure tactic to this route
@check_role("admin")  # Only admins can access this route
@time_limit  # Only accessible between 1 PM and 11 PM
def stats_service():
    return redirect_to_microservice("http://127.0.0.1:5004/stats")

@app.route('/data', methods=['GET'])
@token_required
@limit_exposure  # Apply the limit exposure tactic to this route
def get_data():
    return jsonify({'message': 'Data accessed successfully!'}), 200

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
