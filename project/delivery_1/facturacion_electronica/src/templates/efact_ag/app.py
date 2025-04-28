import hashlib
import logging
import os
import socket
from functools import wraps

import jwt
import requests
from flask import Flask, jsonify, request

# Configurar el nivel de logging
logging.basicConfig(level=logging.DEBUG)

# Configuración básica de la aplicación Flask
app = Flask(__name__)

# Puerto de escucha del API Gateway
API_GATEWAY_PORT = os.getenv("API_GATEWAY_PORT", 5000)

# Auth host y puerto
AUTH_BACKEND_HOST = os.getenv("AUTH_BACKEND_HOST", "auth_be")
AUTH_BACKEND_PORT = os.getenv("AUTH_BACKEND_PORT", 8040)

# Users Load Balancer host y puerto
USERS_LB_HOST = os.getenv("USERS_LB_HOST", "users_lb")
USERS_LB_PORT = os.getenv("USERS_LB_PORT", 5004)

# Invoice Reading Load Balancer host y puerto
EFACT_READING_LB_HOST = os.getenv("EFACT_READING_LB_HOST", "efact_reading_lb")
EFACT_READING_LB_PORT = os.getenv("EFACT_READING_LB_PORT", 5005)

# Invoice Writing Load Balancer host y puerto
EFACT_WRITING_LB_HOST = os.getenv("EFACT_WRITING_LB_HOST", "efact_writing_lb")
EFACT_WRITING_LB_PORT = os.getenv("EFACT_WRITING_LB_PORT", 5006)


# Endpoint ping para verificar la comunicacion con el API Gateway
@app.route("/ping", methods=["GET"])
def ping():
    return (
        jsonify(
            {
                "status": 200,
                "data": {
                    "Frontend IP": request.remote_addr,
                    "API Gateway IP": socket.gethostbyname(socket.gethostname()),
                },
                "message": "Pong desde el API Gateway",
            }
        ),
        200,
    )


# Endpoint para login
@app.route("/login", methods=["POST"])
def login():
    """Endpoint de autenticación"""
    auth_data = request.get_json()
    if not auth_data or "doc_id" not in auth_data or "password" not in auth_data:
        return jsonify({"error": "Credenciales inválidas doc_id and password required"}), 401

    # Obtiene los datos de autenticación del body de la solicitud
    doc_id = auth_data.get("doc_id")
    password = auth_data.get("password")

    # Llamado al servicio de autenticación
    try:
        logging.debug(f"Requesting auth for doc_id: {doc_id}")
        response = requests.post(
            f"http://{AUTH_BACKEND_HOST}:{AUTH_BACKEND_PORT}/auth",
            json={"doc_id": doc_id, "password": password},
        )
        logging.debug(f"Response from auth service: {response.json()}")
        if response.status_code == 200:
            # Si la autenticación es exitosa, se genera un token JWT
            return response.json()
        else:
            return jsonify({"error": "Credenciales inválidas"}), 401
    except requests.exceptions.RequestException as e:
        logging.error(f"Error al conectar con el servicio de autenticación: {e}")
        return jsonify({"error": "Error en el servicio de autenticación"}), 500


# Endpoint ping para verificar la comunicacion con el microservicio de usuarios
@app.route("/ping-users", methods=["GET"])
def ping_users():
    # Peticion al microservicio de usuarios atraves de un balanceador de carga
    res = requests.get(
        f"http://{USERS_LB_HOST}:{USERS_LB_PORT}/ping"
    )
    return jsonify(res.json()), res.status_code


if __name__ == "__main__":
    # Escucha en todas las interfaces para que Docker lo detecte
    app.run(host="0.0.0.0", port=API_GATEWAY_PORT)
