from flask import Flask, request, jsonify
import jwt
import requests
from functools import wraps
import datetime

app = Flask(__name__)
SECRET_KEY = "your_secret_key"
AUTHORIZED_IP = "127.0.0.1"
AUTH_SERVICE_URL = "http://localhost:5003/login"  # Dirección del auth service

# Limita acceso por IP
def limit_exposure(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_ip = request.remote_addr
        if client_ip != AUTHORIZED_IP:
            return jsonify({'message': 'Forbidden: Unauthorized IP'}), 403
        return f(*args, **kwargs)
    return decorated_function

# Verifica token JWT y su expiración
def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({'message': 'Token is missing!'}), 403
        token = auth_header.split(" ")[1]
        try:
            # Decodificar el token y verificar su expiración
            decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            # Verifica si el token ha expirado
            if datetime.datetime.utcnow() > datetime.datetime.utcfromtimestamp(decoded['exp']):
                return jsonify({'message': 'Token expired!'}), 403
            request.user = decoded
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expired!'}), 403
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid!'}), 403
        return f(*args, **kwargs)
    return decorated_function

# Requiere rol
def role_required(required_role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_role = request.user.get('role')
            if user_role != required_role:
                return jsonify({'message': 'Access denied: insufficient permissions'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Redirige login al auth service
@app.route('/login', methods=['POST'])
def gateway_login():
    try:
        response = requests.post(AUTH_SERVICE_URL, json=request.get_json())
        return jsonify(response.json()), response.status_code
    except requests.ConnectionError:
        return jsonify({'message': 'Auth service unavailable'}), 503

# Ruta protegida
@app.route('/data', methods=['GET'])
@token_required
@limit_exposure
@role_required('admin')
def get_data():
    return jsonify({'message': f"Welcome {request.user['username']}! You have admin access."}), 200

if __name__ == "__main__":
    app.run(port=5000, debug=True)
