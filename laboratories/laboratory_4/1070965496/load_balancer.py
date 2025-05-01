from flask import Flask, request, Response
import requests
import itertools
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

api_gateways = itertools.cycle([
    "http://127.0.0.1:5000",
    "http://127.0.0.1:5003",
    "http://127.0.0.1:5006"
])

@app.route("/<path:path>", methods=["GET", "POST"])
def forward(path):
    target = next(api_gateways)
    url = f"{target}/{path}"
    logging.info(f"Proxying to {url}")

    headers = dict(request.headers)

    if request.method == "GET":
        resp = requests.get(url, headers=headers, params=request.args)
    else:
        resp = requests.post(url, headers=headers, json=request.get_json())

    return Response(resp.content, resp.status_code, resp.headers.items())

if __name__ == "__main__":
    app.run(port=8000, debug=True)