"""
Microservicio Genérico
- Implementa validación de seguridad en dos capas
- Registro de actividad
"""
from flask import Flask, request, jsonify
from auth_utils import token_required, limit_exposure
import os
import ipaddress
from datetime import datetime

app = Flask(__name__)

@app.before_request
def layered_security():
    """Implementa defensa en profundidad"""
    
    #Filtrado por IP
    client_ip = ipaddress.ip_address(request.remote_addr)
    gateway_network = ipaddress.ip_network(os.getenv('GATEWAY_NETWORK', '172.20.0.0/24'))
    
    if client_ip not in gateway_network:
        return jsonify({"error": "Acceso no permitido"}), 403
    
    # Validación de token para rutas protegidas
    if request.path == '/microservice' and 'Authorization' not in request.headers:
        return jsonify({"error": "Autenticación requerida"}), 401

@app.route('/microservice')
@token_required
@limit_exposure
def service_endpoint():
    """Endpoint principal del microservicio"""
    return jsonify({
        "message": "Operación exitosa",
        "service": "microservice-v1.2",
        "timestamp": datetime.utcnow().isoformat(),
        "user": request.current_user['username']
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.getenv('MICRO_SERVICE_PORT', 5001))