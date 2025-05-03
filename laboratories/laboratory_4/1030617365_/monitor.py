from flask import Flask, request, jsonify, render_template_string
import time
import threading
import requests
import json

app = Flask(__name__)

# Métricas
metrics = {
    "api_requests": 0,
    "cache_hits": 0,
    "cache_misses": 0,
    "api_gateway_load": {
        "5000": 0,
        "5003": 0
    },
    "response_times": [],
    "tasks_queued": 0,
    "tasks_completed": 0
}

# Semáforo para sincronización
metrics_lock = threading.Lock()

# Endpoint para recibir metrics
@app.route("/metrics/update", methods=["POST"])
def update_metrics():
    data = request.json
    with metrics_lock:
        # Actualizar métricas específicas
        if "api_requests" in data:
            metrics["api_requests"] += 1
        if "cache_hit" in data and data["cache_hit"]:
            metrics["cache_hits"] += 1
        if "cache_hit" in data and not data["cache_hit"]:
            metrics["cache_misses"] += 1
        if "port" in data:
            metrics["api_gateway_load"][str(data["port"])] += 1
        if "response_time" in data:
            metrics["response_times"].append(data["response_time"])
            # Mantener solo las últimas 100 mediciones
            if len(metrics["response_times"]) > 100:
                metrics["response_times"].pop(0)
        if "task_queued" in data and data["task_queued"]:
            metrics["tasks_queued"] += 1
        if "task_completed" in data and data["task_completed"]:
            metrics["tasks_completed"] += 1
    
    return jsonify({"status": "updated"})

# Dashboard para ver las métricas en formato HTML
@app.route("/dashboard", methods=["GET"])
def dashboard():
    with metrics_lock:
        current_metrics = metrics.copy()
    
    # Calcular métricas adicionales
    cache_ratio = 0
    if (current_metrics["cache_hits"] + current_metrics["cache_misses"]) > 0:
        cache_ratio = current_metrics["cache_hits"] / (current_metrics["cache_hits"] + current_metrics["cache_misses"]) * 100
    
    avg_response_time = 0
    if current_metrics["response_times"]:
        avg_response_time = sum(current_metrics["response_times"]) / len(current_metrics["response_times"])
    
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Performance Monitor</title>
        <meta http-equiv="refresh" content="5">
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .metric-card { border: 1px solid #ddd; border-radius: 5px; padding: 15px; margin: 10px; display: inline-block; width: 200px; }
            .metric-title { font-weight: bold; margin-bottom: 10px; }
            .metric-value { font-size: 24px; color: #333; }
            .good { color: green; }
            .warning { color: orange; }
            .critical { color: red; }
            .flex-container { display: flex; flex-wrap: wrap; }
        </style>
    </head>
    <body>
        <h1>Sistema de Monitoreo de Rendimiento</h1>
        <div class="flex-container">
            <div class="metric-card">
                <div class="metric-title">Peticiones API Total</div>
                <div class="metric-value">{{ metrics.api_requests }}</div>
            </div>
            <div class="metric-card">
                <div class="metric-title">Aciertos de Caché</div>
                <div class="metric-value">{{ metrics.cache_hits }}</div>
            </div>
            <div class="metric-card">
                <div class="metric-title">Fallos de Caché</div>
                <div class="metric-value">{{ metrics.cache_misses }}</div>
            </div>
            <div class="metric-card">
                <div class="metric-title">Ratio de Caché</div>
                <div class="metric-value {{ 'good' if cache_ratio > 70 else 'warning' if cache_ratio > 30 else 'critical' }}">
                    {{ "%.2f"|format(cache_ratio) }}%
                </div>
            </div>
            <div class="metric-card">
                <div class="metric-title">Carga API Gateway 5000</div>
                <div class="metric-value">{{ metrics.api_gateway_load['5000'] }}</div>
            </div>
            <div class="metric-card">
                <div class="metric-title">Carga API Gateway 5003</div>
                <div class="metric-value">{{ metrics.api_gateway_load['5003'] }}</div>
            </div>
            <div class="metric-card">
                <div class="metric-title">Tiempo de Respuesta Promedio</div>
                <div class="metric-value {{ 'good' if avg_response_time < 300 else 'warning' if avg_response_time < 1000 else 'critical' }}">
                    {{ "%.2f"|format(avg_response_time) }} ms
                </div>
            </div>
            <div class="metric-card">
                <div class="metric-title">Tareas en Cola</div>
                <div class="metric-value">{{ metrics.tasks_queued - metrics.tasks_completed }}</div>
            </div>
        </div>
    </body>
    </html>
    """   
    
    return render_template_string(html_template, 
                                  metrics=current_metrics, 
                                  cache_ratio=cache_ratio,
                                  avg_response_time=avg_response_time)

# Ruta para resetear métricas
@app.route("/metrics/reset", methods=["POST"])
def reset_metrics():
    with metrics_lock:
        metrics["api_requests"] = 0
        metrics["cache_hits"] = 0
        metrics["cache_misses"] = 0
        metrics["api_gateway_load"] = {"5000": 0, "5003": 0}
        metrics["response_times"] = []
        metrics["tasks_queued"] = 0
        metrics["tasks_completed"] = 0
    
    return jsonify({"status": "reset"})

# Endpoint para obtener métricas en formato JSON
@app.route("/metrics", methods=["GET"])
def get_metrics():
    with metrics_lock:
        return jsonify(metrics)

if __name__ == "__main__":
    app.run(port=5006, debug=True)