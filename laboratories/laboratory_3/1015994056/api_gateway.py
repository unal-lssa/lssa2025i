from flask import Flask, request, jsonify
import jwt
import requests
from functools import wraps

app = Flask(__name__)
SECRET_KEY = "your_secret_key"
AUTHORIZED_IP = "127.0.0.1"  # Only allow local access

# Mock users
USERS = {
    "user1": "password123",
    "admin": "adminpass"
}

def limit_exposure(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_ip = request.remote_addr
        if client_ip != AUTHORIZED_IP:
            return jsonify({'message': 'Forbidden: Unauthorized IP'}), 403
        return f(*args, **kwargs)
    return decorated_function

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'message': 'Token is missing!'}), 403
        try:
            token = auth_header.split(" ")[1]
            jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except Exception as e:
            print(f"Token decode error: {e}")
            return jsonify({'message': 'Token is invalid!'}), 403
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['POST'])
def login():
    auth = request.get_json()
    username = auth.get('username')
    password = auth.get('password')
    if USERS.get(username) == password:
        token = jwt.encode({'username': username}, SECRET_KEY, algorithm="HS256")
        return jsonify({'token': token})
    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/data', methods=['GET'])
@token_required
@limit_exposure
def get_data():
    return jsonify({'message': 'Data accessed successfully!'}), 200

@app.route('/audit', methods=['GET'])
@token_required
@limit_exposure
def get_audit():
    auth_header = request.headers.get('Authorization')
    token = auth_header.split(" ")[1]
    decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    username = decoded_token.get('username')

    if username != 'admin':
        return jsonify({'message': 'Forbidden: Admins only!'}), 403

    try:
        response = requests.get('http://127.0.0.1:5004/audit')
        return jsonify(response.json()), response.status_code
    except Exception as e:
        print(f"Error contacting audit service: {e}")
        return jsonify({'message': 'Error contacting audit service'}), 500

if __name__ == "__main__":
    app.run(debug=True)
