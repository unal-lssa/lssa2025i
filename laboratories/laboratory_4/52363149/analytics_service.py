from flask import Flask, request, jsonify
from functools import lru_cache

app = Flask(__name__)


# Simulamos una función pesada que se beneficia de caché local
@lru_cache(maxsize=32)
def expensive_analytics(input_value):
    # Simula procesamiento intensivo
    import time

    time.sleep(2)
    return {"input": input_value, "result": f"Análisis de '{input_value}' completo"}


@app.route("/analyze", methods=["GET"])
def analyze():
    param = request.args.get("param")
    if not param:
        return jsonify({"error": "Falta el parámetro 'param'"}), 400

    result = expensive_analytics(param)
    return jsonify(result)


if __name__ == "__main__":
    app.run(port=5005, debug=True)
