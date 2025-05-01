# api_gateway.py
# API Gateway que centraliza control de acceso, cacheo y enrutamiento de tareas.
# Soporta autenticación JWT y procesamiento asíncrono distribuido.

import time
from functools import wraps

import jwt
import requests
from flask import Flask, jsonify, request

app = Flask(__name__)
SECRET_KEY = "secret"  # Clave usada para validar tokens JWT


# Decorador para proteger rutas con autenticación basada en JWT
def token_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({'error': 'Token faltante'}), 403
        try:
            jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except jwt.exceptions.InvalidTokenError:
            return jsonify({'error': 'Token inválido'}), 403
        return f(*args, **kwargs)
    return wrapper


# Endpoint protegido que retorna datos del microservicio con logica del negocio
@app.route("/business", methods=["GET"])
@token_required
def get_business():
    """
    Retorna respuesta del microservicio sincrónico.
    """
    # Llamado al microservice
    bussiness = requests.get("http://microservice:5001/process").json()
    return jsonify(bussiness), 200


# Endpoint protegido que retorna datos, usando cache si está disponible
@app.route("/data", methods=["GET"])
@token_required
def get_data():
    """
    Retorna datos desde caché si existen.
    Si no, consulta a la base de datos y los guarda en la caché.
    """
    key = "my_data"
    cache_url = f"http://cache:5004/cache/{key}"  # Acceso al contenedor por su nombre
    cache_resp = requests.get(cache_url).json()

    if cache_resp.get('value'):
        # Timestamp
        timestamp = time.strftime("%d-%m-%Y %H:%M:%S", time.localtime())
        return jsonify({'cached': True, 'data': cache_resp['value'], 'timestamp': timestamp}), 200

    # Acceso a base de datos si no hay caché
    db_resp = requests.get("http://database:5002/db").json()
    data = db_resp.get('message')

    # Guardar en caché el nuevo valor
    requests.post(cache_url, json={'value': data})

    # Timestamp
    timestamp = time.strftime("%d-%m-%Y %H:%M:%S", time.localtime())
    return jsonify({'cached': False, 'data': data, 'timestamp': timestamp}), 200


# Endpoint protegido para tareas largas (asincrónicas o pesadas)
@app.route("/longtask", methods=["POST"])
@token_required
def long_task():
    """
    Enruta tareas a worker (normal) o parallel_worker (pesada),
    según el flag 'heavy' en el payload.
    """
    payload = request.json
    is_heavy = payload.get("heavy", False)

    if is_heavy:
        print("➡️ Tarea enviada a parallel_worker")
        requests.post("http://parallel_worker:5006/ptask", json=payload)
    else:
        print("➡️ Tarea enviada a worker")
        requests.post("http://worker:5005/task", json=payload)

    return jsonify({'status': f'Tarea encolada correctamente: {payload}'}), 202


# Endpoint protegido para listar las tareas
@app.route("/tasks", methods=["GET"])
@token_required
def get_tasks():
    """
    Retorna la lista de tareas encoladas.
    """
    worker_resp = requests.get("http://worker:5005/tasks").json()
    parallel_worker_resp = requests.get("http://parallel_worker:5006/tasks").json()

    return jsonify({'worker': worker_resp['tasks'], 'parallel_worker': parallel_worker_resp['tasks']}), 200


if __name__ == "__main__":
    # El servicio escucha en el puerto 5000 (ajustado por docker-compose)
    app.run(host="0.0.0.0", port=5000, debug=True)
