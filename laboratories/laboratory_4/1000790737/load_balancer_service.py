from flask import Flask, request, Response
import itertools, requests

app = Flask(__name__)
services = itertools.cycle(["http://service_1:5003", "http://service_2:5004"])


@app.route("/<path:path>", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
def forward(path):
    target = next(services)
    url = f"{target}/{path}"
    resp = requests.request(
        method=request.method,
        url=url,
        headers={key: value for key, value in request.headers if key != "Host"},
        params=request.args,
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False,
    )
    excluded_headers = [
        "content-encoding",
        "content-length",
        "transfer-encoding",
        "connection",
    ]
    headers = [
        (name, value)
        for (name, value) in resp.raw.headers.items()
        if name.lower() not in excluded_headers
    ]
    return Response(resp.content, resp.status_code, headers)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
