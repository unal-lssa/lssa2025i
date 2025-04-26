from flask import Flask, jsonify, request
import jwt
from functools import wraps
import datetime
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import requests

app = Flask(__name__)
SECRET_KEY = "your_secret_key"
AUTHORIZED_IP = ["127.0.0.1", "172.19.0.1"] # Only allow local access for simplicity

# Limiter config
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["10 per minute"]
)

# Mock users for the sake of the example
USERS = {
    "user1": { "password": "password123", "role": "user" },
    "admin": { "password": "adminpass", "role": "admin" },
}

# Function to check if the request comes from an authorized IP address
def limit_exposure(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_ip = request.remote_addr
        print("Client IP:", client_ip)
        if client_ip not in AUTHORIZED_IP:
            return jsonify({'message': 'Forbidden: Unauthorized IP address'}), 403
        return f(*args, **kwargs)
    return decorated_function

# Function to generate JWT token
def token_required(role_required=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = request.headers.get('Authorization')
            if not token:
                return jsonify({'message': 'Token is missing!'}), 403
            try:
                decoded = jwt.decode(token.split()[1], SECRET_KEY, algorithms=["HS256"])
                if role_required and decoded.get("role") != role_required:
                    return jsonify({'message': 'Forbidden: Insufficient role'}), 403
            except Exception as e:
                return jsonify({'message': f'Token error: {str(e)}'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Route for user login (returns a JWT token)
@app.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    auth = request.get_json()
    username = auth.get('username')
    password = auth.get('password')
    user = USERS.get(username)
    if user and user['password'] == password:
        token = jwt.encode({
            'username': username,
            'role': user['role'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }, SECRET_KEY, algorithm="HS256")
        return jsonify({'token': token})
    return jsonify({'message': 'Invalid credentials'}), 401

# Protected route
@app.route('/data', methods=['GET'])
@token_required()
@limit_exposure
def get_data():
    try:
        micro_response = requests.get("http://microservice:5001/microservice").json()
        db_response = requests.get("http://database:5002/db").json()
        return jsonify({
            'message': 'Protected data accessed successfully!',
            'microservice': micro_response,
            'database': db_response
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/analytics', methods=['GET'])
@token_required(role_required="admin")
@limit_exposure
def get_analytics():
    return jsonify({'message': 'Admin analytics data'}), 200

@app.route('/monitoring', methods=['GET'])
@token_required()
@limit_exposure
def get_monitoring():
    current_hour = datetime.datetime.now().hour
    if current_hour < 8 or current_hour > 18:
        return jsonify({'message': 'Access only allowed between 8am and 6pm'}), 403
    return jsonify({'message': 'Monitoring data'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)