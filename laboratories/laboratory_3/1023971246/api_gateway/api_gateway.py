from flask import Flask, request, jsonify
import requests
import jwt
from functools import wraps
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
SECRET_KEY = "your_secret_key"
AUTHORIZED_IP = ["127.0.0.1", "172.18.0.1"] 

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]  
)


USERS = {
    "user1": "password123"
}


def limit_exposure(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_ip = request.remote_addr
        if client_ip not in AUTHORIZED_IP:
            return jsonify({'message': 'Forbidden: Unauthorized IP'}), 403
        return f(*args, **kwargs)
    return decorated_function


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
@limiter.limit("10 per minute")
def get_data():
    res = requests.get("http://microservice:5001/microservice", headers=request.headers)
    if res.status_code != 200:
        return jsonify({'message': 'Error accessing microservice'}), res.status_code
    return jsonify({'message': 'Data accessed successfully!'}), 200

@app.route('/magic', methods=['GET'])
@token_required
@limit_exposure 
@limiter.limit("5 per minute")
def do_something():
    res = requests.get("http://useful_microservice:5002/real_endpoint", headers=request.headers)
    if res.status_code != 200:
        return jsonify({'message': 'Oh shut'}), res.status_code
    return jsonify({'message': 'Finally! A magic endpoint that does not makes sense'}), 200


@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({
        "message": "Rate limit exceeded",
        "error": str(e.description)
    }), 429

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)