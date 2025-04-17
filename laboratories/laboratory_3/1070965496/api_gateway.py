from flask import Flask, request, jsonify
import jwt
from functools import wraps
import requests
from flask_limiter import Limiter

app = Flask(__name__)

SECRET_KEY = "your_secret_key"
AUTHORIZED_IP = "127.0.0.1"

USERS = {
    "user1": {"password": "password123", "role": "admin"},
    "user2": {"password": "pass456", "role": "user"}
}

# ===== FUNCIONES PARA RATE LIMITING =====

def get_user_identifier():
    token = request.headers.get('Authorization', "").replace("Bearer ", "")
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return data.get("username", "anonymous")
    except Exception:
        return "anonymous"

limiter = Limiter(
    key_func=get_user_identifier,
    app=app,
    default_limits=["100 per hour"]
)

# ===== DECORADORES DE SEGURIDAD =====

def limit_exposure(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.remote_addr != AUTHORIZED_IP:
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
            data = jwt.decode(token.split(" ")[1], SECRET_KEY, algorithms=["HS256"])
            request.user = data
        except:
            return jsonify({'message': 'Token is invalid!'}), 403
        return f(*args, **kwargs)
    return decorated_function

# ===== ENDPOINT DE LOGIN =====

@app.route('/login', methods=['POST'])
@limiter.limit("5 per minute", key_func=lambda: request.remote_addr)
def login():
    auth = request.get_json()
    username = auth.get('username')
    password = auth.get('password')
    user = USERS.get(username)
    if user and user['password'] == password:
        token = jwt.encode({'username': username, 'role': user['role']}, SECRET_KEY, algorithm="HS256")
        return jsonify({'token': token})
    return jsonify({'message': 'Invalid credentials'}), 401

# ===== ENDPOINT ORIGINAL: /data =====

@app.route('/data', methods=['GET'])
@token_required
@limiter.limit("100 per hour", key_func=get_user_identifier)
@limit_exposure
def get_data():
    if request.user['role'] != 'admin':
        return jsonify({'message': 'Forbidden: Admins only'}), 403

    # Registrar el acceso en el servicio de logging (puerto 5004)
    requests.post("http://127.0.0.1:5004/log", json={
        "user": request.user['username'],
        "action": "accessed /data"
    })

    return jsonify({'message': 'Data accessed successfully!'}), 200

# ===== NUEVO ENDPOINT: /microservice-data =====

@app.route('/microservice-data', methods=['GET'])
@token_required
@limit_exposure
def microservice_data():
    try:
        # Llamada al microservicio (puerto 5001)
        response = requests.get("http://127.0.0.1:5001/microservice")
        micro_data = response.json()

        # Registrar el acceso en el servicio de logging (puerto 5004)
        requests.post("http://127.0.0.1:5004/log", json={
            "user": request.user['username'],
            "action": "accessed /microservice-data"
        })

        return jsonify({'from_microservice': micro_data}), 200
    except Exception as e:
        return jsonify({'error': 'Microservice unreachable', 'details': str(e)}), 500

# ===== MAIN =====

if __name__ == "__main__":
    app.run(debug=True, port=5000)