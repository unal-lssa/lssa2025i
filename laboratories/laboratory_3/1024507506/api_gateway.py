from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import jwt
import requests
from functools import wraps

app = Flask(__name__)
SECRET_KEY = "your_secret_key"
AUTHORIZED_IP = "127.0.0.1"  # Only allow local access for simplicity


limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100 per hour"]
)
limiter.init_app(app)

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
        if not token:
            return jsonify({'message': 'Token is missing!'}), 403
        try:
            jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except:
            return jsonify({'message': 'Token is invalid!'}), 403
        return f(*args, **kwargs)
    return decorated_function



@app.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    auth_data = request.get_json()
    response = requests.post("http://localhost:5003/auth", json=auth_data)
    return jsonify(response.json()), response.status_code



# Protected route
@app.route('/data', methods=['GET'])
@token_required
@limit_exposure  # Apply the limit exposure tactic to this route
def get_data():
    return jsonify({'message': 'Data accessed successfully!'}), 200

if __name__ == "__main__":
    app.run(debug=True)