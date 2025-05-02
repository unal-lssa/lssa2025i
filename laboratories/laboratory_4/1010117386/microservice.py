from flask import Flask, jsonify
import os

app = Flask(__name__)


@app.route("/process", methods=["GET"])
def process():
    return jsonify({"message": "Business logic executed"}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(port=port, debug=True)
