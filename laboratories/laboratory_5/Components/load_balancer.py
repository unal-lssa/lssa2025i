from flask import Flask, jsonify, request, Response
import itertools
from functools import wraps
import threading
import time
import os
import requests
from Components.status_tracker import register_status

SERVICE_NAME = "LOADBALANCER_AG"

app = Flask(__name__)

api_gateways = itertools.cycle(["http://127.0.0.1:5000", "http://127.0.0.1:5003"])
request_timestamps = []
rate_lock = threading.Lock()

# Decorador para rate limiting
def rate_limited(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        global request_timestamps

        MAX_REQUESTS = int(os.getenv("MAX_REQUESTS_PER_TIME", 2))
        RATE_TIME = int(os.getenv("RATE_LIMIT_TIME", 60))

        now = time.time()
        with rate_lock:
            request_timestamps[:] = [t for t in request_timestamps if now - t < RATE_TIME]
            if len(request_timestamps) >= MAX_REQUESTS:
                print("AG Load Balancer: 'Too many requests, try again later'")
                register_status(SERVICE_NAME, 429)
                return jsonify({'AG Load Balancer': 'Too many login attempts, try again later'}), 429
            else:
                register_status(SERVICE_NAME, 200)
            request_timestamps.append(now)

        return f(*args, **kwargs)
    return decorated_function

@app.route("/<path:path>", methods=["GET", "POST"])
@rate_limited
def forward(path):
    target = next(api_gateways)
    url = f"{target}/{path}"

    # Reenviamos headers excepto 'Host'
    headers = {key: value for key, value in request.headers if key.lower() != 'host'}

    # Reenvía la petición original al destino
    response = requests.request(
        method=request.method,
        url=url,
        headers=headers,
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False
    )

    # Devolvemos la respuesta original
    return Response(response.content, status=response.status_code, headers=dict(response.headers))

if __name__ == "__main__":
    app.run(port=8000, debug=True)
