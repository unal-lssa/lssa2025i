from flask import Flask, request, Response
import itertools
import requests
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)


CANDIDATE_INSTANCES = [
    "http://api-gateway-1:5000",
    "http://api-gateway-2:5000",
    "http://api-gateway-3:5000",
]


def check_instance_health(url):
    try:
        health_resp = requests.get(f"{url}/health", timeout=2)
        return health_resp.status_code == 200
    except requests.RequestException:
        return False


def initialize_live_instances():
    live = []
    for url in CANDIDATE_INSTANCES:
        if check_instance_health(url):
            logging.info(f"✓ Instance {url} is healthy.")
            live.append(url)
        else:
            logging.warning(f"✗ Instance {url} is unreachable.")
    if not live:
        logging.error("🚫 No API Gateway instances are reachable. Exiting.")
        exit(1)
    return itertools.cycle(live)


api_gateways = initialize_live_instances()


@app.route("/<path:path>", methods=["GET", "POST"])
def forward(path):
    target = next(api_gateways)
    full_url = f"{target}/{path}"
    logging.info(f"→ Forwarding to: {full_url}")

    try:
        if request.method == "GET":
            resp = requests.get(full_url, headers=request.headers, params=request.args)
        elif request.method == "POST":
            resp = requests.post(
                full_url, headers=request.headers, json=request.get_json()
            )
        else:
            return Response("Method Not Allowed", status=405)
    except requests.RequestException as e:
        logging.error(f"❌ Error forwarding to {full_url}: {e}")
        return Response("Gateway Error", status=502)

    excluded_headers = [
        "content-encoding",
        "content-length",
        "transfer-encoding",
        "connection",
    ]
    headers = [
        (k, v) for k, v in resp.raw.headers.items() if k.lower() not in excluded_headers
    ]
    return Response(resp.content, status=resp.status_code, headers=headers)


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8000,
        debug=False,
        threaded=True
    )
