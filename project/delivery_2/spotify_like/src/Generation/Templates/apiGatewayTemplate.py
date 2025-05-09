import os, textwrap


def generate_api_gateway(
    name: str,
    output_dir="skeleton",
    route_map: dict[str, str] = None,
):
    path = f"{output_dir}/{name}"
    os.makedirs(path, exist_ok=True)

    route_entries = ",\n        ".join(
        [
            f'"{service.replace("_lb", "")}": "http://{service}:{component_port}"'
            for service, component_port in route_map.items()
        ]
    )

    main_py = textwrap.dedent(
        f"""
        from fastapi import FastAPI, Request, HTTPException
        import httpx

        app = FastAPI()

        ROUTE_MAP = {{
            {route_entries}
        }}

        @app.api_route("/{{full_path:path}}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
        async def proxy(full_path: str, request: Request):
            method = request.method
            headers = dict(request.headers)
            body = await request.body()

            path_parts = full_path.split("/", 1)
            if not path_parts or path_parts[0] == '':
                return {{
                    "status_code": 200,
                    "content": "API-GATEWAY RUNNING CORRECTLY"
                }}

            service = path_parts[0]
            remaining_path = path_parts[1] if len(path_parts) > 1 else ""

            target_url = ROUTE_MAP.get(service)
            if not target_url:
                raise HTTPException(status_code=404, detail=f"Unknown service: {{service}}")

            # Forward the request to backend service
            proxy_url = f"{{target_url}}/{{remaining_path}}"

            async with httpx.AsyncClient() as client:
                response = await client.request(method, proxy_url, headers=headers, content=body)

            return {{
                "status_code": response.status_code,
                "content": response.json() if 'application/json' in response.headers.get('content-type', '') else response.text
            }}
    """
    )

    with open(os.path.join(path, "main.py"), "w") as f:
        f.write(main_py)

    dockerfile = textwrap.dedent(
        """
        FROM python:3.11-slim

        WORKDIR /app
        COPY . .

        RUN pip install --no-cache-dir -r requirements.txt

        CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
    """
    )

    with open(os.path.join(path, "Dockerfile"), "w") as f:
        f.write(dockerfile)

    # Create requirements.txt
    requirements = textwrap.dedent(
        """
        fastapi
        uvicorn
        httpx
    """
    )

    with open(os.path.join(path, "requirements.txt"), "w") as f:
        f.write(requirements)
