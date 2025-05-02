from flask import Flask, jsonify

from utils.logger import setup_logger

# Configurar el logger
logger = setup_logger("Database", "database.log")

app = Flask(__name__)

@app.route("/db", methods=["GET"])
def db_data():
    logger.info(f"Solicitud recibida base dedatos  >>>>>>> [/db]")   
    return jsonify({'message': 'Fetched fresh data from DB'})

if __name__ == "__main__":
     app.run(host="0.0.0.0",port=5002, debug=True)
