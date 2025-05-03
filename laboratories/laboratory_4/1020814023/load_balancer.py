from flask import Flask, request, jsonify
import requests
import itertools

app = Flask(__name__)

api_gateways = itertools.cycle(["http://127.0.0.1:5000", "http://127.0.0.1:5003", "http://127.0.0.1:5006"])

@app.route("/<path:path>", methods=["GET", "POST"])
def forward(path):
    target = next(api_gateways)
    url = f"{target}/{path}"
    headers = dict(request.headers)
    try:
        if request.method == "POST":
            data = request.get_json()
            response = requests.post(url, json=data, headers=headers)
        else:
            response = requests.get(url, headers=headers)
        return jsonify(response.json()), response.status_code

    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=8000, debug=True)
