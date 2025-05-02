from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Simulación de base de datos simple
DATABASE = {"message": "Fetched fresh data from DB"}


@app.route("/db", methods=["GET"])
def get_data():
    # Aquí puedes incluir la lógica para obtener datos desde un servicio de caché o base de datos
    return jsonify(DATABASE)


@app.route("/longtask", methods=["POST"])
def long_task():
    data = request.get_json()
    # Aquí debes procesar la tarea larga
    return jsonify({"status": "Task received", "task_data": data})


if __name__ == "__main__":
    app.run(port=5002, debug=True)
