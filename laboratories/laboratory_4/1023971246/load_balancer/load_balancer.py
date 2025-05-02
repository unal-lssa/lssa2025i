from flask import Flask, redirect
import itertools

app = Flask(__name__)
api_gateways = itertools.cycle(["http://127.0.0.1:5000", "http://127.0.0.1:5003"])

@app.route("/<path:path>", methods=["GET", "POST"])
def forward(path):
    target = next(api_gateways)
    return redirect(f"{target}/{path}", code=307)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)