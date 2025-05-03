from flask import Flask, request, jsonify
import jwt
import os

# Inicializa el microservicio Flask
app = Flask(__name__)

# Secreto interno compartido con el API Gateway
INTERNAL_SECRET = os.getenv("INTERNAL_SECRET", "internal_default")

# Simulación de base de datos en memoria con inventario
inventory_db = {
    "A001": {"name": "Laptop", "stock": 10},
    "B002": {"name": "Keyboard", "stock": 25},
    "C003": {"name": "Mouse", "stock": 40}
}

# Endpoint para consultar el inventario completo
@app.route("/inventory", methods=["GET"])
def get_inventory():
    token = request.headers.get("X-Internal-Token")
    try:
        # Validar que la petición venga desde el API Gateway autorizado
        jwt.decode(token, INTERNAL_SECRET, algorithms=["HS256"])
        return jsonify({"inventory": inventory_db}), 200
    except:
        return jsonify({"message": "Unauthorized internal access"}), 403

# Punto de entrada principal del microservicio
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
