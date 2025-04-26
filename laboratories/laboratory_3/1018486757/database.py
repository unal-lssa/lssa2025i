from flask import Flask, jsonify, request
from config import CERTIFICATE_DB, limit_exposure

app = Flask(__name__)

@app.route('/db')
@limit_exposure
def db_access():
    if request.headers.get('Authorization') != CERTIFICATE_DB:
        return jsonify({'error': 'resource not found'}), 404
    return jsonify(
        {
            'message': 'Database access granted'
        }
    ), 200

if __name__ == "__main__":
    app.run(debug=True, port=5002)
