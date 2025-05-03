from flask import Flask, jsonify, request, redirect
import itertools
from config import CERTIFICATE_PAY

app = Flask(__name__)
api_gateways = itertools.cycle(["http://127.0.0.1:5003", "http://127.0.0.1:5007", "http://127.0.0.1:5008"])


@app.route("/<path:path>", methods=["GET", "POST"])
def forward(path):
    if request.headers.get('Authorization') != CERTIFICATE_PAY:
        return jsonify({'error': 'resource not found'}), 404
    target = next(api_gateways)

    print(f"Forwarding request to {target}")
    return redirect(f"{target}/{path}", code=307)


if __name__ == "__main__":
    app.run(port=8001, debug=True)
