from flask import Flask, request, jsonify
import jwt
from functools import wraps

app = Flask(__name__)
SECRET_KEY = "your_secret_key"
AUTHORIZED_IP = "127.0.0.1"  # Only allow local access for simplicity

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

# Function to check JWT token
def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        print(token)
        if not token:
            return jsonify({'message': 'Token is missing!'}), 403
        try:
            jwt.decode(token.split(" ")[1], SECRET_KEY, algorithms=["HS256"])
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
@limit_exposure  # Apply the limit exposure tactic to this route
def get_data():
    return jsonify({'message': 'Data accessed successfully!'}), 200

if __name__ == "__main__":
    app.run(debug=True)