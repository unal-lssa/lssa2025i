"""
Microservicio de Base de Datos
- Valida IPs autorizadas
- Verifica token JWT
- Implementa control de acceso
"""
from flask import Flask, request, jsonify
from auth_utils import token_required, role_required
import os
import ipaddress

app = Flask(__name__)

@app.before_request
def security_validations():
    """Validaciones de seguridad en capa de servicio"""
    # 1. Validación de IP origen
    client_ip = ipaddress.ip_address(request.remote_addr)
    allowed_ips = [ipaddress.ip_network(ip.strip()) for ip in os.getenv('ALLOWED_IPS').split(',')]
    
    if not any(client_ip in network for network in allowed_ips):
        return jsonify({"error": "IP no autorizada"}), 403
    
    # 2. Validación de token (si la ruta lo requiere)
    if request.path == '/db' and 'Authorization' not in request.headers:
        return jsonify({"error": "Token requerido"}), 401

@app.route('/db')
@token_required
@role_required('admin')
def db_access():
    """Endpoint para operaciones de base de datos"""
    return jsonify({
        "message": "Acceso a DB concedido",
        "user": request.current_user['username'],
        "operations": ["query", "update", "delete"]
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.getenv('DB_SERVICE_PORT', 5002))