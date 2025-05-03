from flask import Flask, request, Response
import itertools, requests

app = Flask(__name__)
workers = itertools.cycle(["http://worker_1:5008", "http://worker_2:5009"])


@app.route("/task", methods=["POST"])
def forward():
    target = next(workers)
    url = f"{target}/task"
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
    app.run(host="0.0.0.0", port=5007, debug=True)
