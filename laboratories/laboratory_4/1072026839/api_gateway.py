from flask import Flask, request, jsonify
import jwt, requests
from functools import wraps
import time
import uuid

app = Flask(__name__)
SECRET_KEY = "secret"
instance_id = str(uuid.uuid4())[:8] # ID único para esta instancia

# Decoradores
def token_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token: 
            return jsonify({'error': 'Missing token'}), 403
        try: 
            jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except: 
            return jsonify({'error': 'Invalid token'}), 403
        return f(*args, **kwargs)
    return wrapper

# Acceso a datos con caché TTL
@app.route("/data", methods=["GET"])
@token_required
def get_data():
    cache_resp = requests.get("http://127.0.0.1:5004/cache/my_data").json()
    
    if cache_resp.get('cached', False) and cache_resp['value']:
        return jsonify({
            'cached': True, 
            'data': cache_resp['value'], 
            'from_instance': instance_id
        })
    
    # Si no está en caché o expiró, obtener de BD
    db_resp = requests.get("http://127.0.0.1:5002/db").json()
    
    # Guardar en caché con TTL de 30 segundos
    requests.post(
        "http://127.0.0.1:5004/cache/my_data", 
        json={
            'value': db_resp['message'],
            'ttl': 30 # TTL en segundos
        }
    )
    
    return jsonify({
        'cached': False, 
        'data': db_resp['message'],
        'from_instance': instance_id
    })

# Ruta al balanceador de microservicios
@app.route("/process", methods=["GET"])
@token_required
def process_request():
    # Redirigir al balanceador de carga de microservicios
    response = requests.get("http://127.0.0.1:8001/process")
    
    # Añadir información de esta instancia
    result = response.json()
    result['api_gateway_instance'] = instance_id
    
    return jsonify(result)

# Ruta al balanceador de workers
@app.route("/longtask", methods=["POST"])
@token_required
def long_task():
    payload = request.json
    
    # Redirigir al balanceador de carga de workers
    response = requests.post(
        "http://127.0.0.1:8002/task", 
        json=payload
    )
    
    result = response.json()
    result['api_gateway_instance'] = instance_id
    
    return jsonify(result), 202

if __name__ == "__main__":
    # El puerto se debe pasar como argumento
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    print(f"API Gateway iniciando en puerto {port} (Instance ID: {instance_id})")
    app.run(port=port, debug=True)