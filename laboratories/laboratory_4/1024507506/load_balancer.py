from flask import Flask, request, redirect, Response
import itertools
import requests


app = Flask(__name__)
api_gateways = itertools.cycle(["http://127.0.0.1:5000", "http://127.0.0.1:5003"])

@app.route("/<path:path>", methods=["GET", "POST"])
def proxy(path):
    target = next(api_gateways)
    url = f"{target}/{path}"

    headers = {key: value for key, value in request.headers if key != 'Host'}
    data = request.get_data()

    resp = requests.request(
        method=request.method,
        url=url,
        headers=headers,
        data=data,
        cookies=request.cookies,
        allow_redirects=False,
    )

    return Response(resp.content, status=resp.status_code, headers=dict(resp.headers))

"""
def forward(path):
    target = next(api_gateways)
    return redirect(f"{target}/{path}", code=307)
"""
if __name__ == "__main__":
    app.run(port=8000, debug=True)