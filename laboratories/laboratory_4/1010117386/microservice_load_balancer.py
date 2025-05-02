from flask import Flask, request, Response
import itertools
import requests
import os

app = Flask(__name__)
microservices = itertools.cycle(["http://127.0.0.1:5001", "http://127.0.0.1:5007"])


@app.route("/<path:path>", methods=["GET", "POST"])
def forward(path):
    target = next(microservices)
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
    port = int(os.environ.get("PORT", 5008))
    app.run(port=port, debug=True)
