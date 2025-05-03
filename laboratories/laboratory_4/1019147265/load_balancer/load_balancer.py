from flask import Flask, request, Response
import itertools
import requests  # Add this import
import random

app = Flask(__name__)
api_gateways = itertools.cycle(["http://api_gateway:5000", "http://api_gateway_2:5000"])


# Adjust the full_path to remove the prefix (e.g., 'round_robin/')
@app.route("/round_robin/<path:path>", methods=["GET", "POST"])
async def round_robin(path):
    path = path.split("/")[-1] if "/" in path else path
    target = next(api_gateways)
    url = f"{target}/{path}"
    print(f"Connecting to: {url}")

    headers = {key: value for key, value in request.headers}
    data = request.get_data()

    # Forward the request to the target API gateway
    response = requests.request(  # Use requests library here
        method=request.method,
        url=url,
        headers=headers,
        data=data,
        params=request.args
    )

    # Return the response from the target API gateway
    return Response(
        response.content,
        status=response.status_code,
        headers=dict(response.headers)
    )

# Adjust the full_path to remove the prefix for all functions

@app.route("/random/<path:path>", methods=["GET", "POST"])
async def random_balancer(path):
   
    path = path.split("/")[-1] if "/" in path else path
    target = random.choice(["http://api_gateway:5000", "http://api_gateway:5000"])
    url = f"{target}/{path}"
    headers = {key: value for key, value in request.headers}
    data = request.get_data()

    # Forward the request to the target API gateway
    response = requests.request(  # Use requests library here
        method=request.method,
        url=url,
        headers=headers,
        data=data,
        params=request.args
    )

    # Return the response from the target API gateway
    return Response(
        response.content,
        status=response.status_code,
        headers=dict(response.headers)
    )


@app.route("/weighted_round_robin/<path:path>", methods=["GET", "POST"])
async def weighted_round_robin(path):
    
    path = path.split("/")[-1] if "/" in path else path
    #Added extra http://api_gateway:5000 to the list to give it a higher weight
    api_gateways = itertools.cycle(["http://api_gateway:5000","http://api_gateway:5000", "http://api_gateway_2:5000"])

    target = next(api_gateways)

    url = f"{target}/{path}"
    headers = {key: value for key, value in request.headers}
    data = request.get_data()

    # Forward the request to the target API gateway
    response = requests.request(  # Use requests library here
        method=request.method,
        url=url,
        headers=headers,
        data=data,
        params=request.args
    )

    # Return the response from the target API gateway
    return Response(
        response.content,
        status=response.status_code,
        headers=dict(response.headers)
    )

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)