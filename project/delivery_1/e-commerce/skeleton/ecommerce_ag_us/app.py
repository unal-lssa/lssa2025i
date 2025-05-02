
 from fastapi import FastAPI, Request, HTTPException
 import httpx
 import random
 from fastapi.middleware.cors import CORSMiddleware
 import uvicorn

 app = FastAPI(title="E-commerce API Gateway")

 # Add CORS middleware
 app.add_middleware(
     CORSMiddleware,
     allow_origins=["*"],
     allow_credentials=True,
     allow_methods=["*"],
     allow_headers=["*"],
 )

 # Service registry - mapping endpoints to available services
 SERVICE_REGISTRY = {
     'systems': ['ecommerce_be_or', 'ecommerce_be_pd', 'ecommerce_be_inv'],
     'create': ['ecommerce_be_or'], 
     'process': ['ecommerce_be_pmt']
 }

 # Define direct service routes
 SERVICE_ROUTES = {
     'ecommerce_be_or': 'http://ecommerce_be_or:80',
     'ecommerce_be_pd': 'http://ecommerce_be_pd:80',
     'ecommerce_be_inv': 'http://ecommerce_be_inv:80',
     'ecommerce_be_pmt': 'http://ecommerce_be_pmt:80'
 }

 # Select service using simple round-robin load balancing
 def get_service_for_endpoint(endpoint):
     services = SERVICE_REGISTRY.get(endpoint)
     if not services:
         return None
     return random.choice(services)

 # Generic route handler for proxying requests
 async def proxy_request(target_service, request: Request, path: str):
     method = request.method
     target_url = f"{SERVICE_ROUTES[target_service]}/{path}"

     # Get request body for methods that might have one
     body = None
     if method in ["POST", "PUT", "PATCH"]:
         body = await request.json()

     # Get query parameters
     params = dict(request.query_params)

     # Get headers (excluding host)
     headers = dict(request.headers)
     if "host" in headers:
         del headers["host"]

     # Create httpx client
     async with httpx.AsyncClient() as client:
         try:
             if method == "GET":
                 response = await client.get(target_url, params=params, headers=headers)
             elif method == "POST":
                 response = await client.post(target_url, json=body, params=params, headers=headers)
             elif method == "PUT":
                 response = await client.put(target_url, json=body, params=params, headers=headers)
             elif method == "DELETE":
                 response = await client.delete(target_url, params=params, headers=headers)
             elif method == "PATCH":
                 response = await client.patch(target_url, json=body, params=params, headers=headers)
             else:
                 raise HTTPException(status_code=405, detail="Method not allowed")

             return response.json()
         except httpx.RequestError as e:
             raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")

 @app.get("/systems")
 async def get_systems(request: Request):
     service = get_service_for_endpoint('systems')
     if not service:
         raise HTTPException(status_code=404, detail="Service not found")
     return await proxy_request(service, request, "systems")

 @app.post("/create")
 async def create_system(request: Request):
     service = get_service_for_endpoint('create')
     if not service:
         raise HTTPException(status_code=404, detail="Service not found")
     return await proxy_request(service, request, "create")

 @app.post("/process")
 async def process_payment(request: Request):
     service = get_service_for_endpoint('process')
     if not service:
         raise HTTPException(status_code=404, detail="Service not found")
     return await proxy_request(service, request, "process")

 # Dynamic service routes
@app.api_route("/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
 async def service_routes(service: str, path: str, request: Request):
     if service not in SERVICE_ROUTES:
         raise HTTPException(status_code=404, detail=f"Service '{service}' not found")
     return await proxy_request(service, request, path)

 @app.get("/health")
 async def health_check():
     return {"status": "API Gateway is healthy"}

 if __name__ == "__main__":
     uvicorn.run("app:app", host="0.0.0.0", port=80, reload=True)
