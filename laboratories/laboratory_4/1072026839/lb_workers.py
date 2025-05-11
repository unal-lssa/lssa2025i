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