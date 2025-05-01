# cache.py
# Servicio simple de almacenamiento en caché en memoria.
# Expone una API REST con operaciones GET, POST y DELETE.

from flask import Flask, jsonify, request

app = Flask(__name__)

# Diccionario en memoria para simular la caché
cache = {}


@app.route("/cache/<key>", methods=["GET"])
def get_cache(key):
    """
    Retorna el valor asociado a una clave en la caché.
    Si no existe, devuelve 'value': null.
    """
    value = cache.get(key)
    return jsonify({'value': value}), 200


@app.route("/cache/<key>", methods=["POST"])
def set_cache(key):
    """
    Almacena un valor bajo una clave específica.
    Requiere un cuerpo JSON con el campo "value".
    """
    data = request.json
    value = data.get("value")
    cache[key] = value
    return jsonify({'status': 'ok'}), 201


@app.route("/cache/<key>", methods=["DELETE"])
def delete_cache(key):
    """
    Elimina una clave de la caché.
    Útil para pruebas o reinicializaciones.
    """
    if key in cache:
        del cache[key]
        return jsonify({'status': 'deleted'}), 200
    return jsonify({'status': 'not found'}), 404


if __name__ == "__main__":
    # El servicio escucha en el puerto 5004 (como definido en docker-compose)
    app.run(host="0.0.0.0", port=5004, debug=True)
