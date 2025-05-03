from flask import Flask, request, redirect
import itertools

app = Flask(__name__)
api_gateways = itertools.cycle(["http://127.0.0.1:5000", "http://127.0.0.1:5006"])


@app.route("/<path:path>", methods=["GET", "POST"])
def forward(path):
    target = next(api_gateways)
    print(f"Forwarding request to {target}")
    return redirect(f"{target}/{path}", code=307)


if __name__ == "__main__":
    app.run(port=8000, debug=True)
