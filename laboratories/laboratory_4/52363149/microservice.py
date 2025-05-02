from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Simular una base de datos simple
DATABASE = {"message": "Fetched fresh data from DB"}


@app.route("/db", methods=["GET"])
def get_data():
    cache_resp = requests.get("http://127.0.0.1:5004/cache/my_data").json()
    if cache_resp.get("value"):
        return jsonify({"cached": True, "data": cache_resp["value"]})
    # Simular DB fetch
    db_resp = DATABASE
    # Almacenar en caché local
    requests.post(
        "http://127.0.0.1:5003/cache/my_data", json={"value": db_resp["message"]}
    )
    return jsonify({"cached": False, "data": db_resp["message"]})


@app.route("/longtask", methods=["POST"])
def long_task():
    data = request.get_json()
    # Redirigir al worker
    response = requests.post("http://127.0.0.1:5006/task", json=data)
    return jsonify({"worker_response": response.json()}), response.status_code


if __name__ == "__main__":
    app.run(port=5001, debug=True)
