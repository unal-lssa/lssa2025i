"""
API Gateway - Punto único de entrada

Controla:
- Autenticación
- Enrutamiento
- Limitación de exposición
"""
from flask import Flask, request, jsonify
import os
from auth_utils import token_required, limit_exposure, role_required, generate_token

app = Flask(__name__)

users = {
        'admin': {'password': os.getenv('ADMIN_PASS'), 'role': 'admin'},
        'user1': {'password': os.getenv('USER_PASS'), 'role': 'user'},
        'vendedor': {'password': os.getenv('VEN_PASS'), 'role': 'vendedor'},
    }

@app.route('/authenticate', methods=['GET'])
@limit_exposure
def authenticate():
    """Endpoint de autenticación"""
    auth_data = request.get_json()
    if not auth_data or 'username' not in auth_data or 'password' not in auth_data:
        return jsonify({"error": "Credenciales inválidas"}), 401
    
    # Obtiene los datos de autenticación del body de la solicitud  
    user = users.get(auth_data.get('username'))    
    # TODO: Realizar la conexión con base de datos para validar usuario
    if user and user['password'] == auth_data.get('password'):
        return jsonify({'username': auth_data['username'], 'role': user['role']}),200
    return jsonify({"error": "Credenciales inválidas."}), 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.getenv('AUTH_SERVICE_PORT', 5004))
    print(f"Starting API Gateway on port {os.getenv('AUTH_SERVICE_PORT', 5004)}")