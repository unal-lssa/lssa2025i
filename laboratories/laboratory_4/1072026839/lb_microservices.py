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