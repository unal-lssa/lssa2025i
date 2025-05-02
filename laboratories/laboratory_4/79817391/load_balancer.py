from flask import Flask, request, redirect
import itertools
import os

from utils.logger import setup_logger

# Configurar el logger
logger = setup_logger("Load Balancer", "load_balancer.log")

API_GATEWAY_1 = os.getenv("API_GATEWAY_1_URL", "http://127.0.0.1:5000")
API_GATEWAY_2 = os.getenv("API_GATEWAY_2_URL", "http://127.0.0.1:5003")


app = Flask(__name__)
api_gateways = itertools.cycle([API_GATEWAY_1, API_GATEWAY_2])

@app.route("/<path:path>", methods=["GET", "POST"])
def forward(path):
    logger.info(f"Solicitud recibida load balancer  >>>>>>>  {path}")   
    target = next(api_gateways)
    logger.info(f"  >>> Target   >>>>>>>  {target}")       
    return redirect(f"{target}/{path}", code=307)

if __name__ == "__main__":
     app.run(host="0.0.0.0",port=8000, debug=True)