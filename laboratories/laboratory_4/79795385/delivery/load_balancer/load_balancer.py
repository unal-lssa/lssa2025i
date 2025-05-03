from flask import Flask, request, redirect
import itertools

app = Flask(__name__)
api_gateways = itertools.cycle(["http://api_gateway1:5000", "http://api_gateway2:5000"])

@app.route("/<path:path>", methods=["GET", "POST"])
def forward(path):
    # Get the query parameters from the incoming request
    query_string = request.query_string.decode("utf-8")
    target = next(api_gateways)
    
    # Forward the request to the next API gateway, appending the query string if it exists
    if query_string:
        return redirect(f"{target}/{path}?{query_string}", code=307)
    else:
        return redirect(f"{target}/{path}", code=307)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)
    # app.run(port=8000, debug=True)