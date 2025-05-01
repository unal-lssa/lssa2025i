# microservice.py
# Microservicio simple que simula una operación sincrónica de negocio.

import time

from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/process", methods=["GET"])
def process():
    """
    Simula una operación de lógica de negocio rápida.
    Retorna una respuesta estática indicando éxito.
    """
    # Timestamp
    timestamp = time.strftime("%d-%m-%Y %H:%M:%S", time.localtime())
    return jsonify({'message': f'Lógica de negocio ejecutada correctamente: {timestamp}'}), 200

if __name__ == "__main__":
    # El microservicio expone su API en el puerto 5001
    app.run(host="0.0.0.0", port=5001, debug=True)
