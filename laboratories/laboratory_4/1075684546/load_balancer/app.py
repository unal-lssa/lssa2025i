import threading
import time
import logging
from flask import Flask, request, redirect, Response
import itertools

import requests

app = Flask(__name__)
api_gateways = [
    "http://api_gateway_1:5000",
    "http://api_gateway_2:5006",
    "http://api_gateway_3:5007",
    "http://api_gateway_4:5008",
    "http://api_gateway_5:5009"
]

gateway_status = {gw: {"healthy": False, "latency": float("inf")} for gw in api_gateways}

def check_gateway_heatlh():
    while True:
        for gw in api_gateways:
            try:
                start_time = time.time()
                r = requests.get(f"{gw}/health")
                latency = time.time() - start_time
                if r.status_code == 200:
                    gateway_status[gw]["healthy"] = True
                    gateway_status[gw]["latency"] = latency
                    logging.info(f"Gateway {gw} is healthy with latency {latency}")
                else:
                    gateway_status[gw]["healthy"] = False
                    logging.error(f"Gateway {gw} is unhealthy")
            except Exception as e:
                gateway_status[gw]["healthy"] = False
                logging.error(f"Gateway {gw} is unhealthy: {e}")
        time.sleep(5)

with app.app_context():
    threading.Thread(target=check_gateway_heatlh, daemon=True).start()

@app.route("/<path:path>", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
def forward(path):
    healthy_gateways = [gw for gw in api_gateways if gateway_status[gw]["healthy"]]
    if not healthy_gateways:
        logging.error("No healthy gateways available")
        return "No healthy gateways available", 503
    best_gateway = min(healthy_gateways, key=lambda gw: gateway_status[gw]["latency"])
    
    url = f"{best_gateway}/{path}"
    resp = requests.request(
        method=request.method,
        url=url,
        headers={key: value for key, value in request.headers if key != 'Host'},
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False
    )

    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in excluded_headers]
    response = Response(resp.content, resp.status_code, headers)
    return response

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)