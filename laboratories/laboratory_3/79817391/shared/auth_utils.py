"""
Módulo de utilidades de seguridad


Incluye decoradores para:
- Validación de JWT
- Control de acceso por IP
- Gestión de roles
"""
import os
import jwt
import ipaddress
from functools import wraps
from flask import request, jsonify
from datetime import datetime, timedelta

def token_required(f):
    """ Valida la presencia y 
        validez del token JWT
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').split('Bearer ')[-1]
        if not token:
            return jsonify({"error": "Token requerido"}), 401
        
        try:
            payload = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=["HS256"])
            request.current_user = payload
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expirado"}), 401
        except Exception as e:
            return jsonify({"error": f"Token inválido: {str(e)}"}), 401
            
        return f(*args, **kwargs)
    return decorated

def limit_exposure(f):
    """Restringe el acceso 
        por direcciones IP autorizadas
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        client_ip = ipaddress.ip_address(request.remote_addr)
        allowed_ips = [ipaddress.ip_network(ip.strip()) for ip in os.getenv('ALLOWED_IPS').split(',')]
        
        if not any(client_ip in network for network in allowed_ips):
            return jsonify({"error": f"Acceso denegado para IP {client_ip}"}), 403
        
        return f(*args, **kwargs)
    return decorated

def role_required(role):
    """Valida el rol del usuario"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if request.current_user.get('role') != role:
                return jsonify({"error": "Permisos insuficientes"}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator

def generate_token(user_data):
    """Genera token JWT con expiración"""
    user_data['exp'] = datetime.utcnow() + timedelta(minutes=int(os.getenv('TOKEN_EXPIRATION_MIN', 30)))
    return jwt.encode(user_data, os.getenv('SECRET_KEY'), algorithm="HS256")