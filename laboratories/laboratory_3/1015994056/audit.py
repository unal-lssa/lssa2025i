from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/audit')
def audit():
    return jsonify({'message': 'This is a secure audit service, accessible only to admins.'}), 200

if __name__ == "__main__":
    app.run(debug=True, port=5004)
