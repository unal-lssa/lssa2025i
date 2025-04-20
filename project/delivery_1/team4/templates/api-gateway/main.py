import yaml
import jwt
import requests
from flask import Flask, request, jsonify
from datetime import datetime, timedelta
from functools import wraps

# 1) Carga de configuración
def load_config(path="config.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)

cfg = load_config()
JWT_SECRET = cfg["jwt_secret"]
ROUTES     = cfg["routes"]

# Usuario por defecto
USERS = {
    "user": "123456"
}

app = Flask(__name__)

# 2) Decorador de autenticación JWT
def jwt_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return jsonify({"message": "Missing or malformed Authorization header"}), 401
        token = auth.split()[1]
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            request.user = payload
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid token"}), 401
        return f(*args, **kwargs)
    return wrapper

# 3) Ruta “catch‑all” para proxy dinámico
@app.route("/<path:path>", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
@jwt_required
def gateway(path):
    # Extraer prefijo: /users, /orders, etc.
    prefix = "/" + path.split("/")[0]
    if prefix not in ROUTES:
        return jsonify({"message": f"Service {prefix} not found"}), 404

    backend_base = ROUTES[prefix]["backend"]
    # Asegura que tenga esquema
    if not backend_base.startswith(("http://", "https://")):
        backend_base = "http://" + backend_base
    rest_of_path = "/".join(path.split("/")[1:])
    url = f"{backend_base}/{rest_of_path}"
    print(url)

    # Reenviar la petición
    resp = requests.request(
        method=request.method,
        url=url,
        headers={k: v for k, v in request.headers if k != "Host"},
        params=request.args,
        json=request.get_json(silent=True),
        timeout=5
    )
    return (resp.text, resp.status_code, resp.raw.headers.items())

# 4) Endpoints de utilidad
@app.route("/__health", methods=["GET"])
def health():
    return jsonify({"status": "OK"}), 200

@app.route("/__reload", methods=["POST"])
@jwt_required
def reload_config():
    global cfg, JWT_SECRET, ROUTES
    cfg = load_config()
    JWT_SECRET = cfg["jwt_secret"]
    ROUTES     = cfg["routes"]
    return jsonify({"message": "Configuration reloaded"}), 200

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")
    # Validar credenciales
    if USERS.get(username) != password:
        return jsonify({"message": "Credenciales inválidas"}), 401
    # Generar token con expiración a 30 min
    exp = datetime.utcnow() + timedelta(minutes=30)
    token = jwt.encode(
        {"sub": username, "exp": exp},
        JWT_SECRET,
        algorithm="HS256"
    )
    return jsonify({"token": token}), 200

if __name__ == "__main__":
    # Corre en 0.0.0.0 para Docker y configuraciones de red
    app.run(host="0.0.0.0", port=5000, debug=True)
