from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import requests
from functools import wraps
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
limiter = Limiter(
    get_remote_address,
    app=app,
)

# Function to check JWT token
def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 403
        response = requests.post('http://auth_ms:80/validate_token', json={'token': token.split(' ')[1]}, timeout=5)
        if response.status_code != 200:
            return jsonify({'message': 'Token is invalid!'}), 403
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 403
        response = requests.get('http://auth_ms:80/is_admin', headers={'Authorization': token}, timeout=5)
        if response.status_code != 200:
            return jsonify({'message': 'Admin privileges required!'}), 403
        return f(*args, **kwargs)
    return decorated_function

# Route for user login (returns JWT token)
@app.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    print('login')
    auth = request.get_json()
    username = auth.get('username')
    password = auth.get('password')
    response = requests.post('http://auth_ms:80/login', json={'username': username, 'password': password}, timeout=5)
    if response.status_code == 200:
        token = response.json().get('token')
        return jsonify({'token': token}), 200
    if response.status_code == 403:
        return jsonify({'message': 'Forbidden: Unauthorized IP'}), 403
    else:
        return jsonify({'message': f'Invalid credentials > {response.text}'}), 401
    
@app.route('/register', methods=['POST'])
@limiter.limit("5 per minute")
def register():
    auth = request.get_json()
    username = auth.get('username')
    password = auth.get('password')
    role = auth.get('role')
    first_name = auth.get('first_name')
    last_name = auth.get('last_name')
    email = auth.get('email')
    if not username or not password or not first_name or not last_name or not email:
        return jsonify({'message': 'Missing required fields'}), 400

    # Register user in auth service
    user_id = os.urandom(16).hex()
    response = requests.post('http://auth_ms:80/register', json={'id': user_id,'username': username, 'password': password, 'role': role}, timeout=5)
    if response.status_code == 201:
        # Register user in users service
        user_response = requests.post(
            'http://users_ms:80/createUser',
            json={
                'id': user_id,
                'username': username,
                'first_name': first_name,
                'last_name': last_name,
                'email': email
            },
            timeout=5
        )
        if user_response.status_code == 201:
            return jsonify({'message': 'User registered successfully'}), 201
        else:
            return jsonify({'message': 'User created in auth but failed in users service'}), 500
    if response.status_code == 403:
        return jsonify({'message': 'Forbidden: Unauthorized IP'}), 403
    else:
        return jsonify({'message': 'User registration failed'}), 400

@app.route('/getUserData', methods=['GET'])
@token_required
@limiter.limit("100 per minute")
def get_user_data():
    token = request.headers.get('Authorization')
    user_response = requests.get('http://auth_ms:80/getUser', headers={'Authorization': token}, timeout=5)
    user_auth_data = user_response.json()
    username = user_auth_data.get('id')
    response = requests.get(f'http://users_ms:80/getUserById/{username}', timeout=5)
    if response.status_code == 200:
        user_data = response.json()
        return jsonify(user_data), 200
    if response.status_code == 403:
        return jsonify({'message': 'Forbidden: Unauthorized IP'}), 403
    else:
        return jsonify({'message': 'User not found'}), 404
    
@app.route('/getAllUsers', methods=['GET'])
@limiter.limit("5 per minute")
@token_required
@admin_required
def get_all_users():
    response = requests.get('http://users_ms:80/getAllUsers', timeout=5)
    if response.status_code == 200:
        return jsonify(response.json()), 200
    if response.status_code == 403:
        return jsonify({'message': 'Forbidden: Unauthorized IP'}), 403
    else:
        return jsonify({'message': 'Error fetching users'}), 500
    
@app.route('/getUserByUsername/<id>', methods=['GET'])
@token_required
@admin_required
def get_user_by_id(id):
    response = requests.get(f'http://users_ms:80/getUserById/{id}', timeout=5)
    if response.status_code == 200:
        return jsonify(response.json()), 200
    if response.status_code == 403:
        return jsonify({'message': 'Forbidden: Unauthorized IP'}), 403
    else:
        return jsonify({'message': f'User not found - {id}'}), 404

@app.route("/add", methods=["POST"])
@limiter.limit("100 per minute")
def add_task():
    payload = request.json
    if not all(k in payload for k in ("a", "b")):
        return jsonify({'error': 'Missing parameters'}), 400
    # Trigger async task
    response = requests.post("http://worker_ms:80/add", json=payload)
    data = response.json()
    if response.status_code == 201:
        return jsonify({'task_id': data['result_id']}), 201
    else:
        return jsonify({'error': 'Task failed'}), 500

@app.route("/result/<task_id>", methods=["GET"])
@limiter.limit("10 per minute")
def get_result(task_id):
    # Check task status
    response = requests.get(f"http://worker_ms:80/result/{task_id}")
    if response.status_code == 200:
        result = response.json()
        return jsonify(result), 200
    else:
        return jsonify({'error': 'Task not found'}), 404


@app.route('/')
def index():
    return jsonify({'message': 'Welcome to the API Gateway!'}), 200

# Protected route
@app.route('/data', methods=['GET'])
@token_required
def get_data():
    return jsonify({'message': 'Data accessed successfully!'}), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)