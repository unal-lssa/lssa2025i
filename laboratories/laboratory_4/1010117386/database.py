from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/db/<element>", methods=["GET"])
def db_data(element):
    message = "Fetched resource " + element + " from DB"
    return jsonify({"message": message})


if __name__ == "__main__":
    app.run(port=5002, debug=True)
