import logging
import os

import requests
from auth_utils import generate_token  # type: ignore
from flask import Flask, jsonify, request

# Configurar el nivel de logging
logging.basicConfig(level=logging.DEBUG)

# Configuración básica de la aplicación Flask
app = Flask(__name__)

# Puerto de escucha del Servicio de Autenticación
AUTH_BACKEND_PORT = os.getenv("AUTH_BACKEND_PORT", 8040)

# Users Load Balancer host y puerto
USERS_LB_HOST = os.getenv("USERS_LB_HOST", "users_lb")
USERS_LB_PORT = os.getenv("USERS_LB_PORT", 5004)


# Endpoint de autenticación
@app.route("/auth", methods=["POST"])
def authenticate():
    """Endpoint de autenticación"""
    auth_data = request.get_json()
    if not auth_data or "doc_id" not in auth_data or "password" not in auth_data:
        return jsonify({"error": "Credenciales inválidas doc_id and password required"}), 401

    # Obtiene los datos de autenticación del body de la solicitud
    doc_id = auth_data.get("doc_id")
    password = auth_data.get("password")

    # Llamado al servicio de autenticación
    try:
        response = requests.post(
            f"http://{USERS_LB_HOST}:{USERS_LB_PORT}/auth",
            json={"doc_id": doc_id, "password": password},
        )
        if response.status_code == 200:
            # Si la autenticación es exitosa, se genera un token JWT
            user_data = response.json()
            token = generate_token({"doc_id": user_data["doc_id"], "role_name": user_data["role_name"]})
            return jsonify({"token": token}), 200
        else:
            return jsonify({"error": "Credenciales inválidas"}), 401
    except requests.exceptions.RequestException as e:
        logging.error(f"Error al conectar con el servicio de autenticación: {e}")
        return jsonify({"error": "Error en el servicio de autenticación"}), 500


if __name__ == "__main__":
    # Escucha en todas las interfaces para que Docker lo detecte
    app.run(host="0.0.0.0", port=AUTH_BACKEND_PORT)
