# Laboratorio 4 - Escalabilidad

## Carlos Alberto Arevalo Martinez
## C.C. 1.072.026.839

## Descripción

Para el desarrollo del Laboratorio 4, se utilizó la arquitectura escalable brindada y se mejoró para que empleara diversas tácticas de rendimiento y patrones de balanceo de carga. Se extendió el diseño original incorporando tres balanceadores de carga diferentes (Round Robin para API Gateways, Weighted Round Robin para microservicios y Least Connections para workers), se añadió una tercera instancia de API Gateway, se implementaron múltiples microservicios con distintos tiempos de procesamiento, y se incorporó un sistema de caché con política TTL para optimizar el acceso a datos. En el diseño original, nunca se hizo uso del componente microservicios, por lo tanto para esta mejora, en el API Gateway, se adiconó el endpoint "/process" que redirige las solicitudes al balanceador de carga de microservicios, permitiendo una distribución eficiente de las peticiones según la capacidad de cada servicio.

## Mejoras Implementadas

Esta arquitectura mejorada incluye: 

1. **Balanceadores de Carga**
   - `load_balancer.py` - Balanceador principal (Round Robin)
   - `lb_microservices.py` - Balanceador para microservicios (Weighted Round Robin)
   - `lb_workers.py` - Balanceador para workers (Least Connections)
W
2. **API Gateway**
   - `api_gateway.py` - Enrutador de solicitudes con autenticación

3. **Microservicios**
   - `microservice.py` - Lógica de negocio con diferentes tiempos de procesamiento

4. **Procesamiento Asíncrono**
   - `worker.py` - Procesador de tareas asíncronas

5. **Gestión de Datos**
   - `cache_ttl.py` - Servicio de caché con política almacenamiento temporal con expiración automática
   - `database.py` - Simulación de base de datos

## Código Fuente

### Balanceador de Carga Principal (Round Robin)

```python
# load_balancer.py
from flask import Flask, request, redirect
import itertools

app = Flask(__name__)
api_gateways = itertools.cycle([
    "http://127.0.0.1:5000",
    "http://127.0.0.1:5003",
    "http://127.0.0.1:5006" # Nueva instancia de API GATEWAY
])

@app.route("/<path:path>", methods=["GET", "POST"])
def forward(path):
    target = next(api_gateways)
    print(f"Balanceando a: {target}")
    return redirect(f"{target}/{path}", code=307)

if __name__ == "__main__":
    app.run(port=8000, debug=True)
```

### Balanceador de Carga para Microservicios (Weighted Round Robin)

```python
# lb_microservices.py
from flask import Flask, request, redirect
import time

app = Flask(__name__)

# Definición de servicios con pesos
microservices = [
    {"url": "http://127.0.0.1:5001", "weight": 3, "current": 0}, # Mayor capacidad
    {"url": "http://127.0.0.1:5007", "weight": 2, "current": 0}, # Capacidad media
    {"url": "http://127.0.0.1:5008", "weight": 1, "current": 0}  # Menor capacidad
]

total_weight = sum(service["weight"] for service in microservices)

@app.route("/<path:path>", methods=["GET", "POST"])
def forward(path):
    # Algoritmo Weighted Round Robin
    selected = None
    
    for service in microservices:
        service["current"] += service["weight"]
        if selected is None or service["current"] > selected["current"]:
            selected = service
    
    selected["current"] -= total_weight
    print(f"Weighted RR seleccionó: {selected['url']}")
    return redirect(f"{selected['url']}/{path}", code=307)

if __name__ == "__main__":
    app.run(port=8001, debug=True)
```

### Balanceador de Carga para Workers (Least Connections)

```python
# lb_workers.py
from flask import Flask, request, redirect, jsonify
import threading
import time

app = Flask(__name__)

# Servicios con contador de conexiones
workers = [
    {"url": "http://127.0.0.1:5005", "active_connections": 0},
    {"url": "http://127.0.0.1:5009", "active_connections": 0}
]

connection_lock = threading.Lock()

@app.route("/<path:path>", methods=["GET", "POST"])
def forward(path):
    # Algoritmo Least Connections
    with connection_lock:
        # Encontrar worker con menos conexiones
        selected = min(workers, key=lambda x: x["active_connections"])
        selected["active_connections"] += 1
    
    print(f"Least Connections seleccionó: {selected['url']} (conexiones: {selected['active_connections']})")
    
    # Simular finalización de conexión después de un tiempo
    def release_connection():
        time.sleep(5) # Simula duración de la tarea
        with connection_lock:
            selected["active_connections"] -= 1
    
    threading.Thread(target=release_connection).start()
    
    return redirect(f"{selected['url']}/{path}", code=307)

@app.route("/status", methods=["GET"])
def status():
    return jsonify({"workers": workers})

if __name__ == "__main__":
    app.run(port=8002, debug=True)
```

### Caché con política TTL

```python
# cache_ttl.py
from flask import Flask, request, jsonify
import time
import threading

app = Flask(__name__)
cache = {}
DEFAULT_TTL = 30 # Tiempo de vida en segundos

@app.route("/cache/<key>", methods=["GET"])
def get_cache(key):
    if key in cache:
        # Verificar si ha expirado
        if time.time() < cache[key]["expires_at"]:
            print(f"Cache HIT: {key}")
            return jsonify({'value': cache[key]["value"], 'cached': True})
        else:
            # Expiró, eliminar entrada
            print(f"Cache EXPIRED: {key}")
            del cache[key]
    
    print(f"Cache MISS: {key}")
    return jsonify({'value': None, 'cached': False})

@app.route("/cache/<key>", methods=["POST"])
def set_cache(key):
    data = request.json
    ttl = data.get("ttl", DEFAULT_TTL)
    
    cache[key] = {
        "value": data.get("value"),
        "expires_at": time.time() + ttl
    }
    
    print(f"Cache SET: {key} (expira en {ttl}s)")
    return jsonify({'status': 'ok', 'ttl': ttl})

@app.route("/cache/status", methods=["GET"])
def cache_status():
    now = time.time()
    status = {}
    for key, value in cache.items():
        remaining = value["expires_at"] - now
        status[key] = {
            "valid": remaining > 0,
            "remaining_seconds": max(0, remaining)
        }
    return jsonify(status)

if __name__ == "__main__":
    app.run(port=5004, debug=True)
```

### API Gateway

```python
# api_gateway.py
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
```

### Microservicio

```python
# microservice.py
from flask import Flask, jsonify
import uuid
import time

app = Flask(__name__)
instance_id = str(uuid.uuid4())[:8] # ID único

@app.route("/process", methods=["GET"])
def process():
    # Simular carga diferente según el servicio
    # Puerto 5001: carga baja, 5007: carga media, 5008: carga alta
    port = app.config.get('PORT', 5001)
    
    if port == 5001:
        processing_time = 0.2 # Más rápido
    elif port == 5007:
        processing_time = 0.5 # Medio
    else:
        processing_time = 1.0 # Más lento
    
    time.sleep(processing_time)
    
    return jsonify({
        'message': 'Business logic executed', 
        'instance': instance_id,
        'processing_time': processing_time
    }), 200

if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5001
    app.config['PORT'] = port
    print(f"Microservicio iniciando en puerto {port} (Instance ID: {instance_id})")
    app.run(port=port, debug=True)
```

### Worker

```python
# worker.py
from flask import Flask, request, jsonify
import threading
import time
import uuid

app = Flask(__name__)
instance_id = str(uuid.uuid4())[:8] # ID único

@app.route("/task", methods=["POST"])
def handle_task():
    data = request.json
    thread = threading.Thread(target=process_task, args=(data,))
    thread.start()
    
    return jsonify({
        'status': 'Started',
        'worker_instance': instance_id
    }), 202

def process_task(data):
    print(f"Worker {instance_id} procesando tarea: {data}")
    time.sleep(5) # Simular procesamiento
    print(f"Worker {instance_id} completó tarea: {data}")

if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5005
    print(f"Worker iniciando en puerto {port} (Instance ID: {instance_id})")
    app.run(port=port, debug=True)
```

### Base de Datos

```python
# database.py
from flask import Flask, jsonify
import time

app = Flask(__name__)

@app.route("/db", methods=["GET"])
def db_data():
    # Simular retraso de DB
    time.sleep(0.5)
    timestamp = time.strftime("%H:%M:%S")
    return jsonify({
        'message': f'Fetched fresh data from DB at {timestamp}'
    })

if __name__ == "__main__":
    app.run(port=5002, debug=True)
```

## Scripts adicionales recomendados

Para facilitar la ejecución, prueba y gestión de la arquitectura, se recomiendan los siguientes scripts:

### Script para iniciar todos los servicios

```bash
# start_services.sh
#!/bin/bash
# Script para iniciar todos los servicios

# Función para iniciar un servicio en una nueva terminal en Linux
start_service() {
  local command=$1
  local title=$2
  
  if command -v gnome-terminal &> /dev/null; then
    gnome-terminal --title="$title" -- bash -c "$command; read -p 'Presione Enter para cerrar...'"
    return
  fi
  
  # Fallback a background
  echo "Iniciando $title en segundo plano..."
  eval "$command &"
}

echo "Iniciando servicios..."

# Iniciar balanceadores
start_service "python load_balancer.py" "Balanceador Principal (8000)"
sleep 1
start_service "python lb_microservices.py" "Balanceador Microservicios (8001)"
sleep 1
start_service "python lb_workers.py" "Balanceador Workers (8002)"
sleep 1

# Iniciar API Gateways
start_service "python api_gateway.py 5000" "API Gateway 1 (5000)"
sleep 1
start_service "python api_gateway.py 5003" "API Gateway 2 (5003)" 
sleep 1
start_service "python api_gateway.py 5006" "API Gateway 3 (5006)"
sleep 1

# Iniciar microservicios
start_service "python microservice.py 5001" "Microservicio 1 (5001)"
sleep 1
start_service "python microservice.py 5007" "Microservicio 2 (5007)"
sleep 1
start_service "python microservice.py 5008" "Microservicio 3 (5008)"
sleep 1

# Iniciar workers
start_service "python worker.py 5005" "Worker 1 (5005)"
sleep 1
start_service "python worker.py 5009" "Worker 2 (5009)"
sleep 1

# Iniciar servicios de datos
start_service "python cache_ttl.py" "Caché TTL (5004)"
sleep 1
start_service "python database.py" "Base de Datos (5002)"
sleep 1

echo "Todos los servicios iniciados!"
echo "Generando token JWT para pruebas..."

TOKEN=$(python -c "import jwt; print(jwt.encode({'id': 123}, 'secret', algorithm='HS256'))")
echo "TOKEN=${TOKEN}"
echo "Ejemplo de uso:"
echo "curl -X GET -H \"Authorization: ${TOKEN}\" http://127.0.0.1:8000/data"
```

### Script para pruebas automatizadas

```bash
# test_api.sh
#!/bin/bash
# Script para probar la API y los patrones de escalabilidad

# Se necesita un token JWT para la autenticación
TOKEN=$(python -c "import jwt; print(jwt.encode({'id': 123}, 'secret', algorithm='HS256'))")
echo "Token generado: $TOKEN"

echo "1. Probando balanceo Round Robin con API Gateways y Caché TTL"
echo "-----------------------------------------------------------"
echo "Primera solicitud (cache miss):"
curl -s -X GET -H "Authorization: $TOKEN" http://127.0.0.1:8000/data | jq .
echo

echo "Siguientes solicitudes (deberían ser cache hits):"
for i in {1..5}; do
  echo "Solicitud $i:"
  curl -s -X GET -H "Authorization: $TOKEN" http://127.0.0.1:8000/data | jq .
  echo
  sleep 1
done

echo "Estado actual del caché:"
curl -s -X GET http://127.0.0.1:5004/cache/status | jq .
echo

echo "Esperando 31 segundos para que expire el caché..."
sleep 31

echo "Solicitud después de expiración (debería ser cache miss):"
curl -s -X GET -H "Authorization: $TOKEN" http://127.0.0.1:8000/data | jq .
echo

echo "2. Probando balanceo Weighted Round Robin para microservicios"
echo "------------------------------------------------------------"
echo "Enviando 20 solicitudes para ver distribución por peso:"
for i in {1..20}; do
  echo -n "Solicitud $i: "
  curl -s -X GET -H "Authorization: $TOKEN" http://127.0.0.1:8000/process | jq -c '{"instance": .instance, "processing_time": .processing_time}'
  sleep 0.2
done
echo

echo "3. Probando balanceo Least Connections para workers"
echo "------------------------------------------------"
echo "Enviando 8 tareas simultáneas:"
for i in {1..8}; do
  echo "Iniciando tarea $i..."
  curl -s -X POST -H "Content-Type: application/json" -H "Authorization: $TOKEN" \
       -d "{\"task\": \"report-$i\"}" http://127.0.0.1:8000/longtask | jq . &
  sleep 0.5
done

echo "Verificando estado de conexiones en workers:"
sleep 2
curl -s -X GET http://127.0.0.1:8002/status | jq .
sleep 3
echo "Estado actualizado de conexiones:"
curl -s -X GET http://127.0.0.1:8002/status | jq .

echo
echo "Pruebas completadas!"
```

### Script para detener todos los servicios

```bash
# stop_services.sh
#!/bin/bash
# Script para detener todos los servicios

echo "Deteniendo todos los servicios de la arquitectura escalable..."

# Función para buscar y detener procesos por puerto en Linux
kill_process_by_port() {
  local port=$1
  local pid=$(lsof -ti:$port)
  
  if [ -n "$pid" ]; then
    echo "Deteniendo servicio en puerto $port (PID: $pid)..."
    kill $pid
    return 0
  else
    echo "No se encontró ningún proceso en el puerto $port"
    return 1
  fi
}

# Detener balanceadores de carga
kill_process_by_port 8000 # Balanceador principal 
kill_process_by_port 8001 # Balanceador de microservicios
kill_process_by_port 8002 # Balanceador de workers

# Detener instancias de API Gateway
kill_process_by_port 5000 # API Gateway 1
kill_process_by_port 5003 # API Gateway 2
kill_process_by_port 5006 # API Gateway 3

# Detener microservicios
kill_process_by_port 5001 # Microservicio 1
kill_process_by_port 5007 # Microservicio 2
kill_process_by_port 5008 # Microservicio 3

# Detener workers
kill_process_by_port 5005 # Worker 1
kill_process_by_port 5009 # Worker 2

# Detener servicios de datos
kill_process_by_port 5004 # Caché TTL
kill_process_by_port 5002 # Base de datos

# Verificar si quedó algún proceso de Python relacionado
echo "Verificando si hay procesos Python pendientes..."
python_processes=$(ps aux | grep "python" | grep -E "load_balancer|api_gateway|microservice|worker|cache_ttl|database" | grep -v grep)

if [ -n "$python_processes" ]; then
  echo "Procesos Python pendientes encontrados:"
  echo "$python_processes"
  
  read -p "¿Desea terminar todos estos procesos? (s/n): " response
  if [[ "$response" =~ ^[Ss]$ ]]; then
    # Obtener PIDs y terminarlos
    pids=$(echo "$python_processes" | awk '{print $2}')
    for pid in $pids; do
      echo "Terminando proceso $pid..."
      kill $pid
    done
    echo "Procesos terminados."
  else
    echo "Procesos pendientes no terminados."
  fi
else
  echo "No se encontraron procesos Python pendientes."
fi

echo "Todos los servicios han sido detenidos."
```