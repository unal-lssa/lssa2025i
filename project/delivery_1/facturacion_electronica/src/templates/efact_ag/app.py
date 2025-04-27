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


# Táctica de seguridad: Limita acceso por IP
def limit_exposure(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.remote_addr != AUTHORIZED_IP:
            return jsonify({"message": f"Unauthorized IP {request.remote_addr}"}), 403
        return f(*args, **kwargs)

    return decorated


# Táctica de seguridad: Verifica token y roles (JWT)
def token_required(role=None):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = request.headers.get("Authorization")
            if not token:
                return jsonify({"message": "Missing token"}), 403
            try:
                token = token.split(" ")[1] if " " in token else token
                data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
                if role and data.get("role") != role:
                    return jsonify({"message": "Forbidden: Insufficient role"}), 403
                request.user = data
            except:
                return jsonify({"message": "Invalid token"}), 403
            return f(*args, **kwargs)

        return decorated

    return decorator


# Endpoint ping
@app.route("/ping", methods=["GET"])
def ping():
    return (
        jsonify(
            {
                "status": 200,
                "data": {
                    "Client IP": request.remote_addr,
                    "API Gateway IP": socket.gethostbyname(socket.gethostname()),
                },
                "message": "Pong desde el API Gateway",
            }
        ),
        200,
    )


# Endpoint de autenticación y autorización, genera token JWT
@app.route("/auth", methods=["POST"])
def auth():
    auth = request.get_json()
    # LLamado a endpoint para consultar usuario por DOC_ID
    user, res = get_user(auth.get("doc_id"))
    if res.status_code != 200:
        return jsonify({"message": "User not found"}), 404
    # Validacion del password con md5
    md5_password = hashlib.md5(auth.get("password").encode()).hexdigest()
    # Autenticación de usuario
    if user and user["password"] == md5_password:
        token = jwt.encode(
            {"username": user["doc_id"], "role": user["role"]},
            SECRET_KEY,
            algorithm="HS256",
        )
        return jsonify({"token": token})
    return jsonify({"message": "Invalid credentials"}), 401


# Endpoint para registrar usuarios
@app.route("/user", methods=["POST"])
@limit_exposure
@token_required()
def register_user():
    # Paso 1: Peticion al microservicion de registro de usuarios atraves de un balanceador de carga
    # Paso 2: Retornar el resultado al cliente
    # Simulación de registro de un usuario
    internal_token = jwt.encode({}, INTERNAL_SECRET, algorithm="HS256")
    res = requests.post(
        f"http://{USERS_LB_HOST}:{USERS_LB_PORT}/user",
        headers={"X-Internal-Token": internal_token},
    )
    return jsonify(res.json()), res.status_code


# Endpoint para consultar usuarios, solo para admin
@app.route("/users", methods=["GET"])
@limit_exposure
@token_required(role="admin")
def get_users():
    # Paso 1: Peticion al microservicio de usuarios atraves de un balanceador de carga
    # Paso 2: Retornar el resultado al cliente
    # Simulación de consulta de usuarios
    internal_token = jwt.encode({}, INTERNAL_SECRET, algorithm="HS256")
    res = requests.get(
        f"http://{USERS_LB_HOST}:{USERS_LB_PORT}/users",
        headers={"X-Internal-Token": internal_token},
    )
    return jsonify(res.json()), res.status_code


# Endpoint para consultar un usuario por DOC_ID
@app.route("/user/<string:doc_id>", methods=["GET"])
@limit_exposure
@token_required()
def get_user(doc_id):
    # Paso 1: Peticion al microservicio de consulta de usuarios atraves de un balanceador de carga
    # Paso 2: Retornar el resultado al cliente
    # Simulación de consulta de un usuario por DOC_ID
    internal_token = jwt.encode({}, INTERNAL_SECRET, algorithm="HS256")
    res = requests.get(
        f"http://{USERS_LB_HOST}:{USERS_LB_PORT}/user/{doc_id}",
        headers={"X-Internal-Token": internal_token},
    )
    return jsonify(res.json()), res.status_code


# Endpoint para registrar facturas
@app.route("/invoice", methods=["POST"])
@limit_exposure
@token_required()
def register_invoice():
    # Paso 1: Peticion al microservicio de registro de facturas atraves de un balanceador de carga
    # Paso 2: Retornar el resultado al cliente
    # Simulación de registro de una factura
    internal_token = jwt.encode({}, INTERNAL_SECRET, algorithm="HS256")
    res = requests.post(
        f"http://{EFACT_WRITING_LB_HOST}:{EFACT_WRITING_LB_PORT}/invoice",
        headers={"X-Internal-Token": internal_token},
    )
    return jsonify(res.json()), res.status_code


# Endpoint para consultar facturas
@app.route("/invoices", methods=["GET"])
@limit_exposure
@token_required(role="admin")
def get_invoices():
    # Paso 1: Peticion al microservicio de consulta de facturas atraves de un balanceador de carga
    # Paso 2: Retornar el resultado al cliente
    # Simulación de consulta de facturas
    internal_token = jwt.encode({}, INTERNAL_SECRET, algorithm="HS256")
    res = requests.get(
        f"http://{EFACT_READING_LB_HOST}:{EFACT_READING_LB_PORT}/invoices",
        headers={"X-Internal-Token": internal_token},
    )
    return jsonify(res.json()), res.status_code


# Endpoint para consultar una factura por ID_INVOICE
@app.route("/invoice/<string:id_invoice>", methods=["GET"])
@limit_exposure
@token_required(role="admin")
def get_invoice(id_invoice):
    # Paso 1: Peticion al microservicio de consulta de factura por ID_INVOICE atraves de un balanceador de carga
    # Paso 2: Retornar el resultado al cliente
    # Simulación de consulta de una factura por ID_INVOICE
    internal_token = jwt.encode({}, INTERNAL_SECRET, algorithm="HS256")
    res = requests.get(
        f"http://{EFACT_READING_LB_HOST}:{EFACT_READING_LB_PORT}/invoice/{id_invoice}",
        headers={"X-Internal-Token": internal_token},
    )
    return jsonify(res.json()), res.status_code


if __name__ == "__main__":
    # Escucha en todas las interfaces para que Docker lo detecte
    app.run(host="0.0.0.0", port=API_GATEWAY_PORT)
