"""
API Gateway - Punto único de entrada

Controla:
- Autenticación
- Enrutamiento
- Limitación de exposición
"""
import os
import logging
import requests
from flask import Flask, request, jsonify
from datetime import datetime, timedelta
from templates.shared.auth_utils import token_required, limit_exposure, generate_token

# Configurar el nivel de logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

# Configuración desde variables de entorno
SERVICES_CONFIG = {
    'authenticate': {'url': os.getenv('SERVICE_AUTHENTICATE_URL', 'http://localhost:5004/authenticate'), 'role': 'user'},
    'db': {'url': os.getenv('DB_SERVICE_URL'), 'role': 'admin'},
    'data': {'url': os.getenv('DATA_SERVICE_URL'), 'role': 'user'},
    'data/profile': {'url': f"{os.getenv('DATA_SERVICE_URL', 'http://localhost:5005')}/profile", 'role': 'user'},
    'microservice': {'url': os.getenv('MICROSERVICE_URL'), 'role': 'user'}
}
SERVICE_AUTHENTICATE_NAME="authenticate"

@app.route('/login', methods=['POST'])
def login():
    """Autentica usuarios y genera token JWT"""
    try:
        # Obtener el body de la solicitud
        request_body = request.get_json()

        # Configuración del servicio de autenticación
        service_config = SERVICES_CONFIG.get(SERVICE_AUTHENTICATE_NAME)
        logging.debug(f"service_config: {service_config}")
        if not service_config:
            return jsonify({"error": "Servicio de autenticación no configurado"}), 500

        # Llamar al microservicio de autenticación
        response = requests.get(
            service_config['url'],  # URL del microservicio
            json=request_body,  # Pasar el body como JSON
            timeout=5
        )

        # Procesar la respuesta del microservicio
        if response.status_code == 200:
            auth_data = response.json()
            user = auth_data.get('username')
            role = auth_data.get('role')

            if not user or not role:
                return jsonify({"error": "Datos de autenticación incompletos"}), 400

            if user:
                # Generar el token JWT
                token = generate_token({
                    'username': user,
                    'role': role
                })
                return jsonify({"token": token})

            return jsonify({"error": "Credenciales inválidas"}), 401

        return jsonify({"error": "Error en el servicio de autenticación"}), response.status_code

    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Servicio de autenticación no disponible"}), 503
    
    
    
@app.route('/<service_name>', methods=['GET'])
#@token_required
@limit_exposure
def route_service(service_name):
    """Enrutamiento dinámico a microservicios"""
    logging.debug(f"service generico ");
    service_config = SERVICES_CONFIG.get(service_name)
    logging.debug(f"Routing to {service_name} with config: {service_config}")
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
    logging.debug(f"Starting API Gateway on port {os.getenv('GATEWAY_PORT', 5000)}")