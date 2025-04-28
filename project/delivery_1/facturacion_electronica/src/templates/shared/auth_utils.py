import logging
import os
from datetime import datetime, timedelta, timezone
from functools import wraps

import jwt
from flask import jsonify, request

# Configurar el nivel de logging
logging.basicConfig(level=logging.DEBUG)

# Expiración del token
TOKEN_EXPIRATION = 3600  # 1 hora

# Secretos desde variables de entorno
SECRET_KEY = os.getenv("SECRET_KEY", "default_key")
INTERNAL_SECRET = os.getenv("INTERNAL_SECRET", "internal_default")
AUTHORIZED_IP = os.getenv("AUTHORIZED_IP", "127.0.0.1")


# Táctica de seguridad: Limita acceso por IP
def limit_exposure(authorized_ip=AUTHORIZED_IP):
    def wrapper(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if request.remote_addr != authorized_ip:
                logging.warning(f"Unauthorized access attempt from IP: {request.remote_addr}")
                return jsonify({"message": f"Unauthorized IP {request.remote_addr}"}), 403
            return f(*args, **kwargs)
        return decorated
    return wrapper


# Táctica de seguridad: Verifica token y role_name (JWT)
def token_required(role_name=None):
    def wrapper(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = request.headers.get("Authorization")
            logging.debug(f"Token received: {token}")
            if not token:
                logging.warning("Missing token in request headers")
                return jsonify({"message": "Missing token"}), 403
            try:
                token = token.split(" ")[1] if " " in token else token
                data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
                # Obtiene el user_data del token
                user_data = data.get("user")
                if not user_data:
                    logging.warning("Invalid token structure: missing user data")
                    return jsonify({"message": "Invalid token structure"}), 403
                # Verifica el rol del usuario
                if role_name and user_data.get("role_name") != role_name:
                    logging.warning(f"Forbidden access attempt for role_name: {user_data.get('role_name')}")
                    return jsonify({"message": "Forbidden: Insufficient role_name"}), 403
                request.user = user_data
            except Exception as e:
                logging.error(f"Invalid token or token expired: {str(e)}")
                return jsonify({"message": "Invalid token"}), 403
            return f(*args, **kwargs)
        return decorated
    return wrapper


# Táctica de seguridad: Genera un token JWT
def generate_token(user_data, expiration=TOKEN_EXPIRATION):
    """Genera un token JWT con datos del usuario y una fecha de expiración"""
    payload = {
        "user": user_data,
        "exp": datetime.now(timezone.utc) + timedelta(seconds=expiration),
        "iat": datetime.now(timezone.utc)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token
