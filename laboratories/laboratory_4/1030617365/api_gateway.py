from flask import Flask, request, jsonify
import jwt, requests
from functools import wraps
import threading
import time
import os

app = Flask(__name__)
SECRET_KEY = "secret"

# Obtener el puerto del servidor (útil para métricas)
SERVER_PORT = int(os.environ.get("PORT", 5000))

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

def track_metrics(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        # Registrar tiempo de inicio
        start_time = time.time()
        
        # Ejecutar la función original
        result = f(*args, **kwargs)
        
        # Calcular tiempo de ejecución
        execution_time = (time.time() - start_time) * 1000  # en ms
        
        # Enviar métricas al servicio de monitoreo
        try:
            # Extraer información especial si es la respuesta a /data
            cache_hit = False
            if request.path == "/data" and isinstance(result, tuple) and len(result) > 0:
                data = result[0].json
                if 'cached' in data:
                    cache_hit = data['cached']
            
            # Enviar métricas
            requests.post("http://127.0.0.1:5006/metrics/update", 
                         json={
                             "api_requests": 1, 
                             "port": SERVER_PORT,
                             "response_time": execution_time,
                             "cache_hit": cache_hit if request.path == "/data" else None
                         },
                         timeout=0.5)
        except:
            # No bloquear si falla el envío de métricas
            pass
        
        return result
    return wrapper

# Cached data access
@app.route("/data", methods=["GET"])
@token_required
@track_metrics
def get_data():
    # Verificar el caché con opciones mejoradas
    key = "my_data"
    ttl = 60  # Tiempo de expiración en segundos
    
    # Obtener del caché
    cache_resp = requests.get(f"http://127.0.0.1:5004/cache/{key}").json()
    
    if cache_resp['value']:
        return jsonify({'cached': True, 'data': cache_resp['value']})
    
    # Si no está en caché, buscar en la BD y actualizar caché
    db_resp = requests.get("http://127.0.0.1:5002/db").json()
    
    # Almacenar en caché con TTL
    requests.post(f"http://127.0.0.1:5004/cache/{key}", 
                 json={'value': db_resp['message'], 'ttl': ttl})
    
    return jsonify({'cached': False, 'data': db_resp['message']})

# Trigger async task
@app.route("/longtask", methods=["POST"])
@token_required
@track_metrics
def long_task():
    payload = request.json
    
    # Enviar a worker para procesamiento asíncrono
    resp = requests.post("http://127.0.0.1:5005/task", json=payload)
    
    # Actualizar métricas específicas de tareas
    try:
        requests.post("http://127.0.0.1:5006/metrics/update", 
                     json={"task_queued": True},
                     timeout=0.5)
    except:
        pass
    
    return jsonify({'status': 'Task queued', 'task_id': resp.json().get('task_id', None)}), 202

# Endpoint para health checks
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

# Endpoint para generar tokens (para pruebas)
@app.route("/token", methods=["POST"])
def generate_token():
    username = request.json.get('username', 'test_user')
    # Generar token válido por 1 hora
    token = jwt.encode(
        {'user': username, 'exp': time.time() + 3600},
        SECRET_KEY,
        algorithm="HS256"
    )
    return jsonify({'token': token})

# Añadir endpoint de informe de estado
@app.route("/status", methods=["GET"])
def status():
    # Verificar conexiones a servicios dependientes
    services = {
        "database": {"url": "http://127.0.0.1:5002/health", "status": "unknown"},
        "cache": {"url": "http://127.0.0.1:5004/health", "status": "unknown"},
        "worker": {"url": "http://127.0.0.1:5005/health", "status": "unknown"},
        "monitor": {"url": "http://127.0.0.1:5006/health", "status": "unknown"}
    }
    
    for name, service in services.items():
        try:
            response = requests.get(service["url"], timeout=1)
            if response.status_code == 200:
                service["status"] = "healthy"
            else:
                service["status"] = f"unhealthy ({response.status_code})"
        except Exception as e:
            service["status"] = f"unavailable ({str(e)})"
    
    return jsonify({
        "status": "ok",
        "gateway_port": SERVER_PORT,
        "services": services
    })

if __name__ == "__main__":
    import sys
    port = 5000
    if len(sys.argv) > 1 and sys.argv[1] == "--port" and len(sys.argv) > 2:
        port = int(sys.argv[2])
    
    # Establecer el puerto en variable de entorno
    os.environ["PORT"] = str(port)
    
    app.run(port=port, debug=True)