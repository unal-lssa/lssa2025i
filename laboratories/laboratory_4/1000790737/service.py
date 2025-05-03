from flask import Flask, jsonify
import requests

app = Flask(__name__)
CACHE_URL = "http://127.0.0.1:5006/cache/my_data"
DB_URL = "http://127.0.0.1:5005/db"


@app.route("/data", methods=["GET"])
def data():
    cache_resp = requests.get(CACHE_URL).json()
    if cache_resp.get("value"):
        return jsonify({"data": cache_resp["value"]})
    db_resp = requests.get(DB_URL).json()
    value = db_resp.get("message")
    requests.post(CACHE_URL, json={"value": value})
    return jsonify({"data": value})


if __name__ == "__main__":
    import sys

    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5003
    app.run(port=port, debug=True)
