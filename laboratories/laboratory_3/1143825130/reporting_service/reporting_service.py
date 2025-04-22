from flask import Flask, request, jsonify
import jwt
from datetime import datetime
import os

# Inicializa el microservicio Flask
app = Flask(__name__)

# Secreto compartido entre los microservicios para validar tokens internos
INTERNAL_SECRET = os.getenv("INTERNAL_SECRET", "internal_default")

# Simulación de una base de datos con algunas órdenes de prueba
orders_db = [
    {"id": 1, "timestamp": "2024-04-01T10:00:00Z", "status": "CREATED"},
    {"id": 2, "timestamp": "2024-04-02T15:30:00Z", "status": "CREATED"},
    {"id": 3, "timestamp": "2024-04-03T09:10:00Z", "status": "CANCELLED"},
    {"id": 4, "timestamp": "2024-04-04T18:45:00Z", "status": "CREATED"},
]

# Endpoint para generar un reporte estadístico sobre las órdenes
@app.route("/report", methods=["GET"])
def generate_report():
    token = request.headers.get("X-Internal-Token")
    try:
        # Validar que el token provenga del API Gateway (rol admin validado allí)
        jwt.decode(token, INTERNAL_SECRET, algorithms=["HS256"])

        # Generar estadísticas del sistema
        total = len(orders_db)
        created = sum(1 for o in orders_db if o["status"] == "CREATED")
        cancelled = total - created

        report = {
            "generated_at": datetime.utcnow().isoformat(),
            "total_orders": total,
            "created_orders": created,
            "cancelled_orders": cancelled
        }
        return jsonify({"report": report}), 200
    except:
        return jsonify({"message": "Unauthorized internal access"}), 403

# Punto de entrada del microservicio
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003)
