from flask import Flask, request, jsonify
import jwt
import os
from functools import wraps

app = Flask(__name__)
SECRET_KEY = os.getenv("SECRET_KEY", "kS1p_UhHHit_dOmJw1JO1e6PiQLV0xlF7bq5O4U65bw")
AUTHORIZED_IP = os.getenv('AUTHORIZED_IP', '172.18.0.1')
USERS = {
    "user1": "password123"
}


def limit_exposure(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_ip = request.remote_addr
        print(f"Client IP: {client_ip}")  # Debugging line to check client IP
        if client_ip != AUTHORIZED_IP:  
            return jsonify({'message': 'Forbidden: Unauthorized IP'}), 403
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
@limit_exposure # Apply the limit exposure tactic to this route
def get_data():
    return jsonify({'message': 'Data accessed successfully!'}), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)