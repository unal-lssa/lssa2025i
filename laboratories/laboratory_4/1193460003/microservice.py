from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/process", methods=["GET"])
def process():
    return jsonify({'message': 'Business logic executed'}), 200

if __name__ == "__main__":
    app.run(port=5001, debug=True)