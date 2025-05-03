from flask import Flask, jsonify, request
from config import CERTIFICATE_PAY, limit_exposure
from datetime import datetime

app = Flask(__name__)

@app.route('/microservice_pay', methods=['POST'])
@limit_exposure
def microservice():
    print("Headers:", dict(request.headers))
    request_data = request.get_json()

    if not request_data or 'mount' not in request_data or 'card' not in request_data:
        return jsonify({'error': 'Invalid input, mount and card are required'}), 400

    mount = request_data['mount']
    current_date = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

    return jsonify({
        "status": "success",
        "mount": mount,
        "date": current_date
    }), 200

if __name__ == "__main__":
    app.run(debug=True, port=5003)

