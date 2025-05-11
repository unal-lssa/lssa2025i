from flask import Flask, request, Response
import itertools, requests

app = Flask(__name__)
auth_services = itertools.cycle(["http://auth_1:5011", "http://auth_2:5012"])


@app.route("/login", methods=["POST"])
def forward_login():
    target = next(auth_services)
    url = f"{target}/login"
    resp = requests.post(
        url,
        headers={key: value for key, value in request.headers if key != "Host"},
        json=request.get_json(),
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
    app.run(host="0.0.0.0", port=5013, debug=True)
