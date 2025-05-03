from flask import Flask, jsonify, request
from config import CERTIFICATE_MS, AUTHORIZED_IP, limit_exposure

app = Flask(__name__)

@app.route('/microservice')
@limit_exposure
def microservice(): 
    

    if request.headers.get('Authorization') != CERTIFICATE_MS:
        return jsonify({'error': 'resource not found'}), 404   
    return jsonify(
        {
            'message': 'This is a secure microservice'
        }    
    ), 200

@app.route("/process", methods=["GET"])
def process():
    return jsonify({'message': 'Business logic executed'}), 200 

if __name__ == "__main__":
    app.run(debug=True, port=5001)
