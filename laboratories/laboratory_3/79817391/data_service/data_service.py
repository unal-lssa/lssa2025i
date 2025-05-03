"""
Microservicio de Datos para usuarios normales
- Valida IPs del Gateway
- Requiere autenticación JWT
- Registra actividad
"""
from flask import Flask, request, jsonify
from auth_utils import token_required
import os
import ipaddress
from datetime import datetime

app = Flask(__name__)

@app.before_request
def validate_gateway_ip():
    """Valida que el request venga del API Gateway"""
    client_ip = ipaddress.ip_address(request.remote_addr)
    allowed_ips = [ipaddress.ip_network(ip.strip()) for ip in os.getenv('ALLOWED_IPS').split(',')]
    
    if not any(client_ip in network for network in allowed_ips):
        return jsonify({"error": "Acceso denegado: IP no autorizada"}), 403

@app.route('/data')
@token_required
def data_access():
    """Endpoint para datos de usuario normal"""
    print(f"/data data_access")
    return jsonify({
        "message": "Datos de usuario",
        "endpoints": ["/data/profile", "/data/history"],
        "user": request.current_user['username'],
        "timestamp": datetime.utcnow().isoformat()
    })

@app.route('/data/profile')
@token_required
def user_profile():
    """Datos de perfil de usuario"""
    return jsonify({
        "profile": {
            "username": request.current_user['username'],
            "last_access": datetime.utcnow().isoformat(),
            "preferences": {"theme": "dark"}
        }
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.getenv('DATA_SERVICE_PORT', 5003))