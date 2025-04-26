from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/microservice')
def microservice():
    return jsonify({'message': 'This is a secure microservice'}), 200

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5001)
