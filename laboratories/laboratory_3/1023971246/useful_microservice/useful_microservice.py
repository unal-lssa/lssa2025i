from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/real_endpoint')
def microservice():
    return jsonify({'message': 'Of course this is working, what did you expect?'}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)