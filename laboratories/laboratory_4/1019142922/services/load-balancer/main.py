"""Implement a simple Load Balancer"""

import logging
import itertools

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
import httpx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

origins = [
    "http://localhost",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


api_gateways = itertools.cycle(
    [
        "http://api_gateway_1:8000",
        "http://api_gateway_2:8000",
    ]
)


@app.api_route(
    "/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"]
)
async def forward_request(path: str, request: Request):
    target = next(api_gateways)  # Get the next API Gateway instance
    url = f"{target}/{path}"  # Construct the target URL

    logger.info(f"Forwarding request to {target}")

    # Forward the request to the target server
    async with httpx.AsyncClient() as client:
        # Prepare the request to forward
        forwarded_request = client.build_request(
            method=request.method,
            url=url,
            headers=request.headers.raw,
            content=await request.body(),
            params=request.query_params,
        )
        # Send the request and get the response
        response = await client.send(forwarded_request)

    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=response.headers,
    )
