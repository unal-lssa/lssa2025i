from flask import Flask, request, jsonify
import jwt
from functools import wraps
import time
from collections import defaultdict

app = Flask(__name__)
SECRET_KEY = "your_secret_key"
AUTHORIZED_IP = "127.0.0.1"  # Only allow local access for simplicity

# Rate limiting configuration
RATE_LIMIT = 5  # maximum requests per time window
TIME_WINDOW = 60  # time window in seconds (1 minute)
request_counters = defaultdict(list)  # IP address -> list of timestamps

# Mock users for the sake of the example
USERS = {
    "user1": "password123"
}

# Function to check if the request comes from an authorized IP address
def limit_exposure(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_ip = request.remote_addr
        if client_ip != AUTHORIZED_IP:
            return jsonify({'message': 'Forbidden: Unauthorized IP'}), 403
        return f(*args, **kwargs)
    return decorated_function

# Function to detect and prevent service denial (rate limiting)
def detect_service_denial(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_ip = request.remote_addr
        current_time = time.time()
        
        # Remove timestamps older than the time window
        request_counters[client_ip] = [t for t in request_counters[client_ip] if current_time - t < TIME_WINDOW]
        
        # Check if the client has exceeded the rate limit
        if len(request_counters[client_ip]) >= RATE_LIMIT:
            return jsonify({
                'message': 'Too many requests. Please try again later.',
                'retry_after': TIME_WINDOW
            }), 429
        
        # Add the current timestamp to the counter
        request_counters[client_ip].append(current_time)
        
        return f(*args, **kwargs)
    return decorated_function

# Function to check JWT token
def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 403
        try:
            jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except:
            return jsonify({'message': 'Token is invalid!'}), 403
        return f(*args, **kwargs)
    return decorated_function

# Route for user login (returns JWT token)
@app.route('/login', methods=['POST'])
@detect_service_denial  # Apply rate limiting to prevent brute force attacks
def login():
    auth = request.get_json()
    username = auth.get('username')
    password = auth.get('password')
    if USERS.get(username) == password:
        token = jwt.encode({'username': username}, SECRET_KEY, algorithm="HS256")
        return jsonify({'token': token})
    return jsonify({'message': 'Invalid credentials'}), 401

# Protected route
@app.route('/data', methods=['GET'])
@token_required
@limit_exposure 
@detect_service_denial  # Apply rate limiting to prevent DoS attacks
def get_data():
    return jsonify({'message': 'Data accessed successfully!'}), 200
