"""
API Gateway - Punto único de entrada

Controla:
- Autenticación
- Enrutamiento
- Limitación de exposición
"""
from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import requests
import os
from auth_utils import token_required, limit_exposure, role_required, generate_token

app = Flask(__name__)

# Configuración desde variables de entorno
SERVICES_CONFIG = {
    'db': {'url': os.getenv('DB_SERVICE_URL'), 'role': 'admin'},
    'data': {'url': os.getenv('DATA_SERVICE_URL'), 'role': 'user'},
    'data/profile': {'url': f"os.getenv('DATA_SERVICE_URL')/profile", 'role': 'user'},
    'microservice': {'url': os.getenv('MICROSERVICE_URL'), 'role': 'user'}
}

@app.route('/login', methods=['POST'])
def login():
    """Autentica usuarios y genera token JWT"""
    auth_data = request.get_json()
    user = authenticate_user(auth_data)
    
    if user:
        token = generate_token({
            'username': user['username'],
            'role': user['role']
        })
        return jsonify({"token": token})
    
    return jsonify({"error": "Credenciales inválidas"}), 401

@app.route('/userinfo', methods=['GET'])
@token_required
@limit_exposure
def user_info():
    """Endpoint para información de usuario normal"""
    print(f"/userinfo user_info")
    return jsonify({
        'username': request.current_user['username'],
        'role': request.current_user['role'],
        'access_time': datetime.utcnow().isoformat()
    }), 200

@app.route('/<service_name>', methods=['GET'])
@token_required
@limit_exposure
def route_service(service_name):
    """Enrutamiento dinámico a microservicios"""
    print(f"service generico ");
    service_config = SERVICES_CONFIG.get(service_name)
    print(f"Routing to {service_name} with config: {service_config}")
    if not service_config:
        return jsonify({"error": "Servicio no encontrado"}), 404
    
    if request.current_user['role'] != service_config['role']:
        return jsonify({"error": "Acceso no autorizado"}), 403
    
    try:
        response = requests.get(
            service_config['url'],
            headers={'Authorization': request.headers['Authorization']},
            timeout=5
        )
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Servicio {service_name} no disponible."}), 503

def authenticate_user(auth_data):
    """Mock de autenticación - Debe ser implementado con DB real"""
    users = {
        'admin': {'password': os.getenv('ADMIN_PASS'), 'role': 'admin'},
        'user1': {'password': os.getenv('USER_PASS'), 'role': 'user'}
    }
    user = users.get(auth_data.get('username'))
    if user and user['password'] == auth_data.get('password'):
        return {'username': auth_data['username'], 'role': user['role']}
    return None

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.getenv('GATEWAY_PORT', 5000))