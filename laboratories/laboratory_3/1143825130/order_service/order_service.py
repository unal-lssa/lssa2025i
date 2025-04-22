from flask import Flask, request, jsonify
import jwt
from datetime import datetime
import os

# Inicialización del microservicio Flask
app = Flask(__name__)

# Secreto interno para validar tokens desde el API Gateway
INTERNAL_SECRET = os.getenv("INTERNAL_SECRET", "internal_default")

# Simulación de una base de datos de órdenes en memoria
orders_db = []

# Endpoint para registrar una nueva orden
@app.route("/order", methods=["POST"])
def place_order():
    # Validación del token interno
    token = request.headers.get("X-Internal-Token")
    try:
        jwt.decode(token, INTERNAL_SECRET, algorithms=["HS256"])
        # Crear y guardar nueva orden
        new_order = {
            "id": len(orders_db) + 1,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "CREATED"
        }
        orders_db.append(new_order)
        return jsonify({"message": "Order placed", "order": new_order}), 201
    except:
        return jsonify({"message": "Unauthorized internal access"}), 403

# Endpoint para listar todas las órdenes
@app.route("/order", methods=["GET"])
def list_orders():
    token = request.headers.get("X-Internal-Token")
    try:
        jwt.decode(token, INTERNAL_SECRET, algorithms=["HS256"])
        return jsonify({"orders": orders_db}), 200
    except:
        return jsonify({"message": "Unauthorized internal access"}), 403

# Ejecución del microservicio
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
