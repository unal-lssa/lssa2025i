from flask import Flask, jsonify

from utils.logger import setup_logger

# Configurar el logger
logger = setup_logger("Microservice", "microservice.log")


app = Flask(__name__)

@app.route("/process", methods=["GET"])
def process():
    logger.info(f"Solicitud recibida microservicio  >>>>>>>  [/process]") 
    return jsonify({'message': 'Business logic executed'}), 200

if __name__ == "__main__":
     app.run(host="0.0.0.0",port=5001, debug=True)