from flask import Flask, request, Response
import itertools
import requests

app = Flask(__name__)
api_gateways = itertools.cycle(["http://127.0.0.1:5000", "http://127.0.0.1:5003"])


@app.route("/<path:path>", methods=["GET", "POST"])
def forward(path):
    target = next(api_gateways)
    url = f"{target}/{path}"

    # Forward headers (excluding Host)
    headers = {key: value for key, value in request.headers if key.lower() != "host"}

    # Send the request to the target
    resp = requests.request(
        method=request.method,
        url=url,
        headers=headers,
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False,
    )

    # Return the response from the target
    excluded_headers = [
        "content-encoding",
        "content-length",
        "transfer-encoding",
        "connection",
    ]
    response_headers = [
        (name, value)
        for name, value in resp.headers.items()
        if name.lower() not in excluded_headers
    ]

    return Response(resp.content, resp.status_code, response_headers)


if __name__ == "__main__":
    app.run(port=8000, debug=True)
