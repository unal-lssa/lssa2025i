from flask import Flask, request, redirect, jsonify
import random
import time
import requests
import threading

app = Flask(__name__)

# Configuración de instancias de API Gateway
api_gateways = [
    {"url": "http://127.0.0.1:5000", "weight": 1, "active": True, "health": True, "requests": 0, "last_check": 0},
    {"url": "http://127.0.0.1:5003", "weight": 1, "active": True, "health": True, "requests": 0, "last_check": 0},
    # Añadir más instancias para probar mejor el balanceo
    {"url": "http://127.0.0.1:5007", "weight": 1, "active": True, "health": True, "requests": 0, "last_check": 0},
    {"url": "http://127.0.0.1:5008", "weight": 2, "active": True, "health": True, "requests": 0, "last_check": 0}  # Mayor peso, recibirá más tráfico
]

# Variables de configuración
HEALTH_CHECK_INTERVAL = 10  # segundos
algorithm = "round_robin"  # opciones: round_robin, random, weighted, least_connections
current_index = 0  # Para algoritmo round robin

# Mutex para operaciones concurrentes
lock = threading.Lock()

# Funciones de balanceo
def round_robin_select():
    global current_index
    with lock:
        # Buscar la siguiente instancia activa y saludable
        start_index = current_index
        while True:
            current_index = (current_index + 1) % len(api_gateways)
            if api_gateways[current_index]["active"] and api_gateways[current_index]["health"]:
                api_gateways[current_index]["requests"] += 1
                return api_gateways[current_index]["url"]
            # Si hemos revisado todas las instancias y ninguna está disponible
            if current_index == start_index:
                return None

def random_select():
    with lock:
        # Filtrar solo instancias activas y saludables
        available = [gw for gw in api_gateways if gw["active"] and gw["health"]]
        if not available:
            return None
        selected = random.choice(available)
        selected["requests"] += 1
        return selected["url"]

def weighted_select():
    with lock:
        # Crear lista ponderada según los pesos configurados
        weighted_list = []
        for idx, gw in enumerate(api_gateways):
            if gw["active"] and gw["health"]:
                weighted_list.extend([idx] * gw["weight"])
        
        if not weighted_list:
            return None
            
        selected_idx = random.choice(weighted_list)
        api_gateways[selected_idx]["requests"] += 1
        return api_gateways[selected_idx]["url"]

def least_connections_select():
    with lock:
        # Seleccionar la instancia con menos peticiones activas
        available = [(idx, gw) for idx, gw in enumerate(api_gateways) if gw["active"] and gw["health"]]
        if not available:
            return None
            
        min_requests = float('inf')
        selected_idx = -1
        
        for idx, gw in available:
            if gw["requests"] < min_requests:
                min_requests = gw["requests"]
                selected_idx = idx
                
        api_gateways[selected_idx]["requests"] += 1
        return api_gateways[selected_idx]["url"]

# Función para realizar health checks
def health_check():
    while True:
        with lock:
            for gw in api_gateways:
                if gw["active"]:
                    try:
                        start_time = time.time()
                        response = requests.get(f"{gw['url']}/health", timeout=2)
                        if response.status_code == 200:
                            gw["health"] = True
                            gw["last_check"] = time.time()
                        else:
                            gw["health"] = False
                    except:
                        gw["health"] = False
        
        # Esperar hasta el próximo ciclo de health check
        time.sleep(HEALTH_CHECK_INTERVAL)

# Iniciar el thread de health check
health_check_thread = threading.Thread(target=health_check, daemon=True)
health_check_thread.start()

# Endpoint principal para reenviar solicitudes
@app.route("/<path:path>", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
def forward(path):
    # Seleccionar el backend según el algoritmo configurado
    if algorithm == "round_robin":
        target = round_robin_select()
    elif algorithm == "random":
        target = random_select()
    elif algorithm == "weighted":
        target = weighted_select()
    elif algorithm == "least_connections":
        target = least_connections_select()
    else:
        target = round_robin_select()  # Predeterminado
    
    if not target:
        return jsonify({"error": "No hay servidores disponibles"}), 503
    
    # Registrar métricas
    start_time = time.time()
    port = int(target.split(":")[-1])
    
    # Reenviar la solicitud
    response = redirect(f"{target}/{path}", code=307)
    
    # Registrar métricas en el servicio de monitoreo
    end_time = time.time()
    try:
        requests.post("http://127.0.0.1:5006/metrics/update", 
                     json={"api_requests": 1, 
                           "port": port,
                           "response_time": (end_time - start_time) * 1000},  # ms
                     timeout=0.5)
    except:
        pass  # No bloquear si el servicio de métricas no está disponible
    
    return response

# Endpoint de configuración del balanceador
@app.route("/lb/config", methods=["GET", "POST"])
def lb_config():
    global algorithm
    
    if request.method == "POST":
        data = request.json
        if "algorithm" in data:
            algorithm = data["algorithm"]
        
        # Actualizar configuración de instancias
        if "instances" in data:
            with lock:
                for idx, instance in enumerate(data["instances"]):
                    if idx < len(api_gateways):
                        if "active" in instance:
                            api_gateways[idx]["active"] = instance["active"]
                        if "weight" in instance:
                            api_gateways[idx]["weight"] = instance["weight"]
        
        return jsonify({"status": "updated"})
    
    # GET: Devolver configuración actual
    with lock:
        config = {
            "algorithm": algorithm,
            "instances": [
                {
                    "url": gw["url"],
                    "active": gw["active"],
                    "health": gw["health"],
                    "weight": gw["weight"],
                    "requests": gw["requests"]
                } for gw in api_gateways
            ]
        }
    
    return jsonify(config)

# Endpoint para reiniciar estadísticas
@app.route("/lb/reset", methods=["POST"])
def reset_stats():
    with lock:
        for gw in api_gateways:
            gw["requests"] = 0
    
    return jsonify({"status": "reset"})

# Endpoint auxiliar para health checks
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(port=8000, debug=True)