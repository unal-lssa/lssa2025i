from flask import Flask, request, jsonify
import requests
import random
import jwt
from functools import wraps

app = Flask(__name__)
SECRET_KEY = "secret"

# Microservicios que manejan /data y /longtask
microservices = ["http://127.0.0.1:5001", "http://127.0.0.1:5002"]

# Servicio que maneja /db directamente
database_service = "http://127.0.0.1:5003"

# Servicio que maneja /analytics
analytics_service = "http://127.0.0.1:5005"


# Decorador para verificar token JWT
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"error": "Missing token"}), 401
        try:
            jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        return f(*args, **kwargs)

    return decorated


# Ruta /data → microservicio aleatorio
@app.route("/data", methods=["GET"])
@token_required
def route_data():
    service_url = random.choice(microservices)
    try:
        response = requests.get(
            f"{service_url}/data", headers=request.headers, params=request.args
        )
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Error while requesting data: {str(e)}"}), 500


# Ruta /longtask → microservicio aleatorio
@app.route("/longtask", methods=["POST"])
@token_required
def route_longtask():
    service_url = random.choice(microservices)
    try:
        response = requests.post(
            f"{service_url}/longtask", json=request.get_json(), headers=request.headers
        )
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Error while processing long task: {str(e)}"}), 500


# Ruta /db → directo al servicio database.py
@app.route("/db", methods=["GET"])
@token_required
def route_db():
    try:
        response = requests.get(f"{database_service}/db", headers=request.headers)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Error while requesting DB: {str(e)}"}), 500


# Ruta /analytics → directo a analytics_service
@app.route("/analytics", methods=["GET"])
@token_required
def route_analytics():
    try:
        response = requests.get(f"{analytics_service}/analyze", params=request.args)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Error while requesting analytics: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(port=8000, debug=True)
