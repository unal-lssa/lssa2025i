from flask import Flask, jsonify, request
import time
import random
import threading

app = Flask(__name__)

# Datos simulados para diferentes tipos de consultas
mock_data = {
    "users": [
        {"id": 1, "name": "Usuario 1", "email": "usuario1@example.com"},
        {"id": 2, "name": "Usuario 2", "email": "usuario2@example.com"},
        {"id": 3, "name": "Usuario 3", "email": "usuario3@example.com"}
    ],
    "products": [
        {"id": 101, "name": "Producto A", "price": 19.99, "stock": 150},
        {"id": 102, "name": "Producto B", "price": 29.99, "stock": 75},
        {"id": 103, "name": "Producto C", "price": 9.99, "stock": 200},
        {"id": 104, "name": "Producto D", "price": 49.99, "stock": 30}
    ],
    "orders": [
        {"id": 1001, "user_id": 1, "products": [101, 103], "total": 29.98, "date": "2025-03-15"},
        {"id": 1002, "user_id": 2, "products": [102], "total": 29.99, "date": "2025-04-01"},
        {"id": 1003, "user_id": 1, "products": [104], "total": 49.99, "date": "2025-04-20"}
    ]
}

# Configuración de latencia
latency_config = {
    "min_ms": 50,   # Latencia mínima en ms
    "max_ms": 200,  # Latencia máxima en ms
    "instability": 0.0,  # Probabilidad de fallos (0.0 a 1.0)
    "slow_queries": 0.1  # Probabilidad de consultas lentas (0.0 a 1.0)
}

# Mutex para operaciones en la configuración
config_lock = threading.Lock()

# Simulación de latencia variable
def simulate_db_latency():
    with config_lock:
        # Probabilidad de falla
        if random.random() < latency_config["instability"]:
            # Simulación de fallo aleatorio en la BD
            time.sleep(random.uniform(0.5, 2.0))  # Tiempo antes de fallar
            return False
        
        # Probabilidad de consulta lenta
        if random.random() < latency_config["slow_queries"]:
            # Consulta anormalmente lenta
            delay = random.uniform(latency_config["max_ms"] * 2, latency_config["max_ms"] * 5) / 1000
        else:
            # Consulta normal
            delay = random.uniform(latency_config["min_ms"], latency_config["max_ms"]) / 1000
        
        # Aplicar retardo
        time.sleep(delay)
        return True

# Endpoint genérico para simular consulta de base de datos
@app.route("/db", methods=["GET"])
def db_data():
    # Simular comportamiento de la base de datos
    success = simulate_db_latency()
    
    if not success:
        return jsonify({'error': 'Database error'}), 500
    
    # Devolver datos generales
    return jsonify({'message': 'Fetched fresh data from DB'})

# Endpoints para diferentes tipos de datos
@app.route("/db/<data_type>", methods=["GET"])
def get_data_by_type(data_type):
    # Validar tipo de datos solicitado
    if data_type not in mock_data:
        return jsonify({'error': f"Unknown data type '{data_type}'"}), 400
    
    # Simular comportamiento de la base de datos
    success = simulate_db_latency()
    
    if not success:
        return jsonify({'error': 'Database error'}), 500
    
    # Devolver los datos según el tipo solicitado
    return jsonify({'data': mock_data[data_type]})

# Endpoint para consulta por ID
@app.route("/db/<data_type>/<int:item_id>", methods=["GET"])
def get_item_by_id(data_type, item_id):
    # Validar tipo de datos solicitado
    if data_type not in mock_data:
        return jsonify({'error': f"Unknown data type '{data_type}'"}), 400
    
    # Simular comportamiento de la base de datos
    success = simulate_db_latency()
    
    if not success:
        return jsonify({'error': 'Database error'}), 500
    
    # Buscar elemento por ID
    for item in mock_data[data_type]:
        if item["id"] == item_id:
            return jsonify({'data': item})
    
    # No encontrado
    return jsonify({'error': 'Item not found'}), 404

# Endpoint para cambiar configuración de latencia
@app.route("/db/config", methods=["GET", "POST"])
def configure_latency():
    if request.method == "POST":
        data = request.json
        with config_lock:
            # Actualizar la configuración con los parámetros proporcionados
            if "min_ms" in data:
                latency_config["min_ms"] = float(data["min_ms"])
            if "max_ms" in data:
                latency_config["max_ms"] = float(data["max_ms"])
            if "instability" in data:
                # Asegurar que esté entre 0 y 1
                latency_config["instability"] = min(1.0, max(0.0, float(data["instability"])))
            if "slow_queries" in data:
                # Asegurar que esté entre 0 y 1
                latency_config["slow_queries"] = min(1.0, max(0.0, float(data["slow_queries"])))
        
        return jsonify({'status': 'Configuration updated', 'config': latency_config})
    
    # GET: Devolver configuración actual
    return jsonify(latency_config)

# Endpoint para health checks
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(port=5002, debug=True)