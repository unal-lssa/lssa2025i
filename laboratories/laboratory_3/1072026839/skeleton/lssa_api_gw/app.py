
from flask import Flask, request, jsonify
import jwt
from functools import wraps
import requests

app = Flask(__name__)
SECRET_KEY = "your_secret_key"
AUTHORIZED_IP = "127.0.0.1"  # Solo permitir acceso local por simplicidad
LOAD_BALANCER_URL = "http://lssa_lb:80"

# Usuarios de ejemplo para este ejercicio
USERS = {
    "user1": "password123"
}

# Función para verificar si la solicitud proviene de una dirección IP autorizada
def limit_exposure(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_ip = request.remote_addr
        if client_ip != AUTHORIZED_IP:
            return jsonify({'message': 'Forbidden: Unauthorized IP'}), 403
        return f(*args, **kwargs)
    return decorated_function

# Función para verificar el token JWT
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

# Ruta para el inicio de sesión del usuario (devuelve token JWT)
@app.route('/login', methods=['POST'])
def login():
    auth = request.get_json()
    username = auth.get('username')
    password = auth.get('password')

    if USERS.get(username) == password:
        token = jwt.encode({'username': username}, SECRET_KEY, algorithm="HS256")
        return jsonify({'token': token})
    return jsonify({'message': 'Invalid credentials'}), 401

# Ruta protegida para crear un nuevo sistema
@app.route('/create', methods=['POST'])
@token_required
@limit_exposure
def create_system():
    try:
        response = requests.post(f'{LOAD_BALANCER_URL}/create', json=request.get_json())
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'message': f'Error accessing load balancer: {str(e)}'}), 500

# Ruta protegida para obtener todos los sistemas
@app.route('/data', methods=['GET'])
@token_required
@limit_exposure
def get_data():
    try:
        response = requests.get(f'{LOAD_BALANCER_URL}/systems')
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'message': f'Error accessing load balancer: {str(e)}'}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
