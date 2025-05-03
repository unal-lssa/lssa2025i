from flask import Flask, request, jsonify
import jwt
import requests
from functools import wraps

app = Flask(__name__)

SECRET_KEY = "your_secret_key"
AUTHORIZED_IP = "127.0.0.1"

# Decoradores
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
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 403
        try:
            token = token.replace("Bearer ", "")
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            request.user = data
        except Exception:
            return jsonify({'message': 'Token is invalid!'}), 403
        return f(*args, **kwargs)
    return decorated_function

def require_role(role):
    def wrapper(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if request.user.get("role") != role:
                return jsonify({'message': 'Access denied: insufficient role'}), 403
            return f(*args, **kwargs)
        return decorated
    return wrapper

# Auth endpoint
@app.route('/login', methods=['POST'])
def login():
    auth = request.get_json()
    username = auth.get('username')
    password = auth.get('password')

    if username == "admin" and password == "adminpass":
        token = jwt.encode({'username': username, 'role': 'admin'}, SECRET_KEY, algorithm="HS256")
        return jsonify({'token': token})
    elif username == "user1" and password == "userpass":
        token = jwt.encode({'username': username, 'role': 'user'}, SECRET_KEY, algorithm="HS256")
        return jsonify({'token': token})

    return jsonify({'message': 'Invalid credentials'}), 401

# Proxies
@app.route('/user', methods=['GET'])
@token_required
@limit_exposure
def user_service_proxy():
    res = requests.get("http://user_service:5001/", headers=request.headers)
    return jsonify(res.json()), res.status_code

@app.route('/order', methods=['GET'])
@token_required
@limit_exposure
@require_role("admin")
def order_service_proxy():
    res = requests.get("http://order_service:5002/", headers=request.headers)
    return jsonify(res.json()), res.status_code

# Caching pattern
@app.route('/data', methods=['GET'])
@token_required
def cached_data():
    cache_resp = requests.get("http://cache:5004/cache/my_data").json()
    if cache_resp['value']:
        return jsonify({'cached': True, 'data': cache_resp['value']})
    
    db_resp = requests.get("http://order_service:5002/db").json()
    requests.post("http://cache:5004/cache/my_data", json={'value': db_resp['message']})
    return jsonify({'cached': False, 'data': db_resp['message']})

# Async task
@app.route('/longtask', methods=['POST'])
@token_required
def trigger_async_task():
    payload = request.get_json()
    requests.post("http://worker:5005/task", json=payload)
    return jsonify({'status': 'Task queued'}), 202

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)