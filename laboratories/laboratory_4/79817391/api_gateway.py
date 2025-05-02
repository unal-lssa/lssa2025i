from flask import Flask, request, jsonify
import jwt, requests, os
from functools import wraps

from utils.logger import setup_logger

# Configurar el logger
logger = setup_logger("API Gateway", "api_gateway.log")

app = Flask(__name__)
SECRET_KEY = "secret"

# Obtener URLs dinámicas desde las variables de entorno
CACHE_URL = os.getenv("CACHE_URL", "http://127.0.0.1:5004")
DATABASE_URL = os.getenv("DATABASE_URL", "http://127.0.0.1:5002")
WORKER_URL = os.getenv("WORKER_URL", "http://127.0.0.1:5005")

# Decorators (reuse token auth if desired)
def token_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token: return jsonify({'error': 'Missing token'}), 403
        try: jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except: return jsonify({'error': 'Invalid token'}), 403
        return f(*args, **kwargs)
    return wrapper

# Cached data access
@app.route("/data", methods=["GET"])
#@token_required
def get_data():
    
    logger.info("Solicitud recibida en  >>>>>>> /data")   
    
    cache_resp = requests.get(f"{CACHE_URL}/cache/my_data").json()
    logger.info(f"Respuesta  >>>>>>> /cache/my_data {cache_resp}")   
    
    if cache_resp['value']:
        logger.info("Datos obtenidos del caché")
        return jsonify({'cached': True, 'data': cache_resp['value']})
    # Simulate DB fetch
    logger.info("Datos no encontrados en el caché, consultando la base de datos")
    db_resp = requests.get(f"{DATABASE_URL}/db").json()
    requests.post(f"{CACHE_URL}/cache/my_data", json={'value': db_resp['message']})
    logger.info("Datos almacenados en el caché")
    return jsonify({'cached': False, 'data': db_resp['message']})

# Cached data access
@app.route("/clean", methods=["POST"])
#@token_required
def clean_cache():    
    logger.info("Limpiando cache para pruebas")       
    cache_resp = requests.post(f"{CACHE_URL}/cache/clean").json()
    logger.info(f"Cache clean:  >>>>>>> {cache_resp}")   
    return jsonify({'cache_clean': True, 'data': cache_resp['data']})
    

# Trigger async task
@app.route("/longtask", methods=["POST"])
#@token_required
def long_task():
    payload = request.json
    requests.post(f"{WORKER_URL}/task", json=payload)
    return jsonify({'status': 'Task queued'}), 202

if __name__ == "__main__":
    logger.info("main api_gateway")   
    app.run(host="0.0.0.0",port=5000, debug=True)