from flask import Flask, request, jsonify
import jwt
import requests
import os
from functools import wraps

# Configuración básica de la aplicación Flask
app = Flask(__name__)

# Secretos desde variables de entorno
SECRET_KEY = os.getenv("SECRET_KEY", "default_key")
INTERNAL_SECRET = os.getenv("INTERNAL_SECRET", "internal_default")
AUTHORIZED_IP = os.getenv("AUTHORIZED_IP", "127.0.0.1")

# Usuarios del sistema con roles
USERS = {
    "user1": {"password": "password123", "role": "user"},
    "admin": {"password": "adminpass", "role": "admin"}
}

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

# Autenticación de usuarios, genera token JWT
@app.route("/login", methods=["POST"])
def login():
    auth = request.get_json()
    user = USERS.get(auth.get("username"))
    if user and user["password"] == auth.get("password"):
        token = jwt.encode({"username": auth["username"], "role": user["role"]}, SECRET_KEY, algorithm="HS256")
        return jsonify({"token": token})
    return jsonify({"message": "Invalid credentials"}), 401

# Redirige solicitud de orden al microservicio Order
@app.route("/order", methods=["POST"])
@limit_exposure
@token_required()
def place_order():
    internal_token = jwt.encode({}, INTERNAL_SECRET, algorithm="HS256")
    res = requests.post("http://order_service:5001/order", headers={"X-Internal-Token": internal_token})
    return jsonify(res.json()), res.status_code

# Listado de órdenes
@app.route("/orders", methods=["GET"])
@limit_exposure
@token_required()
def list_orders():
    internal_token = jwt.encode({}, INTERNAL_SECRET, algorithm="HS256")
    res = requests.get("http://order_service:5001/order", headers={"X-Internal-Token": internal_token})
    return jsonify(res.json()), res.status_code

# Inventario desde microservicio de inventario
@app.route("/inventory", methods=["GET"])
@limit_exposure
@token_required()
def inventory():
    internal_token = jwt.encode({}, INTERNAL_SECRET, algorithm="HS256")
    res = requests.get("http://inventory_service:5002/inventory", headers={"X-Internal-Token": internal_token})
    return jsonify(res.json()), res.status_code

# Solo para admin: generación de reportes
@app.route("/report", methods=["GET"])
@limit_exposure
@token_required(role="admin")
def report():
    internal_token = jwt.encode({}, INTERNAL_SECRET, algorithm="HS256")
    res = requests.get("http://reporting_service:5003/report", headers={"X-Internal-Token": internal_token})
    return jsonify(res.json()), res.status_code

if __name__ == "__main__":
    # Escucha en todas las interfaces para que Docker lo detecte
    app.run(host="0.0.0.0", port=5000)
