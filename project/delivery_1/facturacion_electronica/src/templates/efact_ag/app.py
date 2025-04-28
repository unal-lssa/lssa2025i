import hashlib
from flask import Flask, request, jsonify
import jwt
import requests
import os
from functools import wraps
import logging

AUTHORIZED_IPS = ["127.0.0.1", "host.docker.internal", "172.17.0.1", "172.18.0.1", "172.19.0.1, 172.21.0.1"]

# Configurar el nivel de logging
logging.basicConfig(level=logging.DEBUG)

# Configuración básica de la aplicación Flask
app = Flask(__name__)

# Secretos desde variables de entorno
SECRET_KEY = os.getenv("SECRET_KEY", "default_key")
INTERNAL_SECRET = os.getenv("INTERNAL_SECRET", "internal_default")
AUTHORIZED_IP = os.getenv("AUTHORIZED_IP", "127.0.0.1")

# Puerto de escucha del API Gateway
API_GATEWAY_PORT = os.getenv("API_GATEWAY_PORT", 5000)

# Users Load Balancer host y puerto
USERS_LB_HOST = os.getenv("USERS_LB_HOST", "users_lb")
USERS_LB_PORT = os.getenv("USERS_LB_PORT", 5004)

# Invoice Reading Load Balancer host y puerto
EFACT_READING_LB_HOST = os.getenv("EFACT_READING_LB_HOST", "efact_reading_lb")
EFACT_READING_LB_PORT = os.getenv("EFACT_READING_LB_PORT", 5005)

# Invoice Writing Load Balancer host y puerto
EFACT_WRITING_LB_HOST = os.getenv("EFACT_WRITING_LB_HOST", "efact_writing_lb")
EFACT_WRITING_LB_PORT = os.getenv("EFACT_WRITING_LB_PORT", 5006)

def limit_exposure(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_ip = request.remote_addr
        if client_ip not in AUTHORIZED_IPS:
            return jsonify({'message': 'Forbidden: Unauthorized IP: ' + client_ip}), 403
        return f(*args, **kwargs)
    return decorated_function

@app.route('/users', methods=['GET', 'POST'])
# @limit_exposure
def proxy_client_data():
    token = request.headers.get("Authorization")
    url = f"http://{USERS_LB_HOST}:{USERS_LB_PORT}"

    try:
        if request.method == 'GET':
            response = requests.get(url, headers={"Authorization": token})
        elif request.method == 'POST':
            response = requests.post(
                url,
                headers={
                    "Authorization": token,
                    "Content-Type": request.headers.get("Content-Type", "application/json")
                },
                json=request.get_json() if request.is_json else None,
                data=request.form if not request.is_json else None
            )
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({"message": f"Error contacting client service: {str(e)}"}), 500

if __name__ == "__main__":
    # Escucha en todas las interfaces para que Docker lo detecte
    app.run(host="0.0.0.0", port=API_GATEWAY_PORT)
