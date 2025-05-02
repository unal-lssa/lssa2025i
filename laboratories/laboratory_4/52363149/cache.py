from flask import Flask, request, jsonify

cache_data = {}

app = Flask(__name__)


@app.route("/cache/my_data", methods=["GET", "POST"])
def handle_cache():
    if request.method == "GET":
        # Retornar los datos en caché si existen
        return jsonify({"value": cache_data.get("my_data")})
    elif request.method == "POST":
        # Guardar los datos en caché
        data = request.json.get("value")
        cache_data["my_data"] = data
        return jsonify({"message": "Data cached successfully"}), 200


if __name__ == "__main__":
    app.run(port=5004, debug=True)
