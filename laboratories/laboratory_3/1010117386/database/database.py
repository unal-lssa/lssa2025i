from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/db")
def db_access():
    return jsonify({"message": "Database response."}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
