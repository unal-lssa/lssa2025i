# database.py
# Servicio que simula una base de datos con una respuesta estática.
# Ideal para pruebas de integración con el API Gateway y caché.

import time

from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/db", methods=["GET"])
def db_data():
    """
    Simula una consulta a base de datos real.
    Se agrega una pequeña latencia para notar el beneficio del cache.
    """
    time.sleep(1)  # Simula acceso a disco o carga desde almacenamiento persistente
    # Timestamp
    timestamp = time.strftime("%d-%m-%Y %H:%M:%S", time.localtime())
    return jsonify({'message': f'Simulación de acceso a la base de datos: {timestamp}'}), 200


if __name__ == "__main__":
    # El servicio escucha en el puerto 5002 para ser accedido por el API Gateway
    app.run(host="0.0.0.0", port=5002, debug=True)
