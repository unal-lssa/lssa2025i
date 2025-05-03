from flask import Flask, request, jsonify
import jwt
from functools import wraps
import requests
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime, timedelta  
from config import CERTIFICATE_PAY, SECRET_KEY, CERTIFICATE_MS, CERTIFICATE_DB, USERS, AUTHORIZED_IP, limit_exposure

app = Flask(__name__)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["10000 per minute"]  
)

def token_required(roles=None):
    if roles is None:
        roles = []

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return jsonify({'message': 'Token is missing!'}), 403
            try:
                token = auth_header.split(" ")[1]
                decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
                user_role = decoded_token.get('username')
                print(user_role)
                print(roles)
                if roles and user_role not in roles:
                    return jsonify({'message': 'Forbidden: Insufficient permissions'}), 403
            except jwt.ExpiredSignatureError:
                return jsonify({'message': 'Token has expired!'}), 403
            except jwt.InvalidTokenError:
                return jsonify({'message': 'Token is invalid!'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator


@app.route('/login', methods=['POST'])
def login():
    auth = request.get_json()
    username = auth.get('username')
    password = auth.get('password')
    if USERS.get(username) == password:
        expiration_time = datetime.now() + timedelta(minutes=600)
        print(expiration_time)
        token = jwt.encode(
            {
                'username': username,
                'exp': expiration_time.timestamp()
            }, 
            SECRET_KEY,
            algorithm="HS256"
        )
        return jsonify({'token': token})
    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/gateway/microservice', methods=['GET'])
@token_required(roles=["user1", "admin"])  
@limiter.limit("5 per minute")
@limit_exposure  
def gateway_microservice():
    headers = {
            'Authorization': CERTIFICATE_MS 
        } 
    try:
        response = requests.get('http://127.0.0.1:5001/microservice', headers=headers)
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({'message': 'Error connecting to microservice', 'error': str(e)}), 500

@app.route('/gateway/db', methods=['GET'])
@token_required(roles=["user1", "admin"])  
@limit_exposure 
def gateway_db():
    headers = {
            'Authorization': CERTIFICATE_DB 
        }

    try:
        response = requests.get('http://127.0.0.1:5002/db', headers=headers)
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({'message': 'Error connecting to database', 'error': str(e)}), 500
    
@app.route('/gateway/microservice_pay', methods=['POST'])
@token_required(roles=["user1", "admin"])
@limiter.limit("5 per minute")
@limit_exposure
def gateway_microservice_pay():   
    try:
        request_data = request.get_json()
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': CERTIFICATE_PAY 
        }        
        response = requests.post(
            'http://127.0.0.1:8001/microservice_pay',
            json=request_data,
            headers=headers
        )
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({'message': 'Error connecting to microservice', 'error': str(e)}), 500
# Cached data access
@app.route("/data", methods=["GET"])
@token_required(roles=["user1", "admin"])
def get_data():
    headers = {
            'Authorization': CERTIFICATE_DB 
        }
    cache_resp = requests.get("http://127.0.0.1:5004/cache/my_data").json()
    if cache_resp['value']:
        print(cache_resp['value'])
        return jsonify({'cached': True, 'data': cache_resp['value']})
     
# Simulate DB fetch 
    db_resp = requests.get("http://127.0.0.1:5002/db", headers=headers).json()
    requests.post("http://127.0.0.1:5004/cache/my_data", json={'value': db_resp['message']}) 
    return jsonify({'cached': False, 'data': db_resp['message']}) 

# Trigger async task
@app.route("/longtask", methods=["POST"])
@token_required(roles=["user1", "admin"])
def long_task():
    payload = request.json 
    requests.post("http://127.0.0.1:5005/task", json=payload) 
    return jsonify({'status': 'Task queued'}), 202 

if __name__ == "__main__":
    app.run(port=5006, debug=True)
    