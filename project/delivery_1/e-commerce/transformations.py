import os, textwrap

def generate_database(name):

    path = f'skeleton/{name}'
    os.makedirs(path, exist_ok=True)

    with open(os.path.join(path, 'init.sql'), 'w') as f:
        f.write(textwrap.dedent("""
            CREATE TABLE IF NOT EXISTS systems (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255)
            );
            """
        ))
        
def generate_mqtp(name, database):
    path = f'skeleton/{name}'
    os.makedirs(path, exist_ok=True)

    with open(os.path.join(path, 'app.py'), 'w') as f:
        f.write(textwrap.dedent(f"""
            from flask import Flask, request, jsonify
            import mysql.connector
            import pika
            import threading
            import json
            import time

            app = Flask(__name__)

            # Setup RabbitMQ connection
            def setup_rabbitmq():
                while True:
                    try:
                        connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
                        channel = connection.channel()
                        channel.queue_declare(queue='payments', durable=True)
                        return connection, channel
                    except Exception as e:
                        print(f"Failed to connect to RabbitMQ: {{e}}")
                        time.sleep(5)

            def start_consumer():
                connection, channel = setup_rabbitmq()
                
                def callback(ch, method, properties, body):
                    payment_data = json.loads(body)
                    process_payment(payment_data)
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                
                channel.basic_consume(queue='payments', on_message_callback=callback)
                print('Payment service started consuming')
                try:
                    channel.start_consuming()
                except Exception as e:
                    print(f"Consumer error: {{e}}")
                    connection.close()
                    time.sleep(5)
                    start_consumer()

            def process_payment(payment_data):
                conn = mysql.connector.connect(
                    host='{database}',
                    user='root',
                    password='root',
                    database='{database}'
                )
                cursor = conn.cursor()
                cursor.execute("INSERT INTO transactions (order_id, amount, status) VALUES (%s, %s, %s)", 
                              (payment_data['order_id'], payment_data['amount'], 'processed'))
                conn.commit()
                cursor.close()
                conn.close()

            @app.route('/process', methods=['POST'])
            def queue_payment():
                data = request.json
                connection, channel = setup_rabbitmq()
                channel.basic_publish(
                    exchange='',
                    routing_key='payments',
                    body=json.dumps(data),
                    properties=pika.BasicProperties(
                        delivery_mode=2,  # make message persistent
                    ))
                connection.close()
                return jsonify(status="payment queued")

            @app.route('/health')
            def health():
                return jsonify(status="ok")

            if __name__ == '__main__':
                # Start consumer in a separate thread
                consumer_thread = threading.Thread(target=start_consumer)
                consumer_thread.daemon = True
                consumer_thread.start()
                
                # Start the Flask app
                app.run(host='0.0.0.0', port=80)
            """
        ))

    with open(os.path.join(path, 'Dockerfile'), 'w') as f:
        f.write(textwrap.dedent("""
            FROM python:3.11-slim
                                
            WORKDIR /app
            COPY . .
            RUN pip install flask mysql-connector-python pika
                                
            CMD ["python", "app.py"]
            """
        ))


def generate_backend(name, database):

    path = f'skeleton/{name}'
    os.makedirs(path, exist_ok=True)

    with open(os.path.join(path, 'app.py'), 'w') as f:
        f.write(textwrap.dedent(f"""
            from flask import Flask, request, jsonify
            import mysql.connector

            app = Flask(__name__)

            @app.route('/create', methods=['POST'])
            def create():
                data = request.json
                conn = mysql.connector.connect(
                    host='{database}',
                    user='root',
                    password='root',
                    database='{database}'
                )
                cursor = conn.cursor()
                cursor.execute("INSERT INTO systems (name) VALUES (%s)", (data['name'],))
                conn.commit()
                cursor.close()
                conn.close()
                return jsonify(status="created")

            @app.route('/systems')
            def get_systems():
                conn = mysql.connector.connect(
                    host='{database}',
                    user='root',
                    password='root',
                    database='{database}'
                )
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM systems")
                rows = cursor.fetchall()
                cursor.close()
                conn.close()
                return jsonify(systems=rows)

            if __name__ == '__main__':
                app.run(host='0.0.0.0', port=80)
            """
        ))

    with open(os.path.join(path, 'Dockerfile'), 'w') as f:
        f.write(textwrap.dedent("""
            FROM python:3.11-slim
                                
            WORKDIR /app
            COPY . .
            RUN pip install flask mysql-connector-python
                                
            CMD ["python", "app.py"]
            """
        ))


def generate_frontend(name, api_gateway):
    
    path = f'skeleton/{name}'
    os.makedirs(path, exist_ok=True)

    with open(os.path.join(path, 'package.json'), 'w') as f:
        f.write(textwrap.dedent("""
            {
                "name": "frontend",
                "version": "1.0.0",
                "main": "app.js",
                "dependencies": {
                    "express": "^4.18.2",
                    "axios": "^1.6.7"
                }
            }
            """
        ))

    with open(os.path.join(path, 'Dockerfile'), 'w') as f:
        f.write(textwrap.dedent("""
            FROM node:18
                                
            WORKDIR /app
            COPY . .
            RUN npm install
                                
            CMD ["node", "app.js"]
            """
        ))

    with open(os.path.join(path, 'app.js'), 'w') as f:
        f.write(textwrap.dedent(f"""
            const express = require('express');
            const axios = require('axios');
            const app = express();
            app.use(express.json());
            app.use(express.urlencoded({{ extended: true }}));

            const API_GATEWAY_URL = 'http://{api_gateway}:80';

            app.get('/', async (req, res) => {{
            try {{
                const response = await axios.get(`${{API_GATEWAY_URL}}/systems`);
                const systems = response.data.systems;
                let list = systems.map(([id, name]) => `<li>${{name}}</li>`).join('');
                res.send(`
                <html>
                    <body>
                    <h1>Frontend</h1>
                    <form method="POST" action="/create">
                        <input name="name" />
                        <button type="submit">Create</button>
                    </form>
                    <ul>${{list}}</ul>
                    </body>
                </html>
                `);
            }} catch (err) {{
                console.error("Error connecting to API Gateway:", err.message);
                res.status(500).send("Error contacting API Gateway");
            }}
            }});

            app.post('/create', async (req, res) => {{
            try {{
                const name = req.body.name;
                await axios.post(`${{API_GATEWAY_URL}}/create`, {{ name }});
                res.redirect('/');
            }} catch (err) {{
                console.error("Error sending data to API Gateway:", err.message);
                res.status(500).send("Error processing your request");
            }}
            }});

            app.get('/health', async (req, res) => {{
                res.status(200).send("Healthcheck OK!");
            }});

            app.listen(80, () => console.log("Frontend running on port 80"));
            """
        ))

def generate_load_balancer(name, frontend_name):
    path = f'skeleton/{name}'
    os.makedirs(path, exist_ok=True)

    with open(os.path.join(path, 'Dockerfile'), 'w') as f:
        f.write(textwrap.dedent("""
            FROM nginx:alpine

            COPY nginx.conf /etc/nginx/nginx.conf
            
            EXPOSE 80

            CMD ["nginx", "-g", "daemon off;"]
        """))

    with open(os.path.join(path, 'nginx.conf'), 'w') as f:
        f.write(textwrap.dedent(f"""
            worker_processes auto;

            events {{
                worker_connections 1024;
            }}

            http {{
                upstream frontend {{
                    server {frontend_name}:80;
                }}

                server {{
                    listen 80;
                    
                    location / {{
                        proxy_pass http://frontend;
                        proxy_set_header Host $host;
                        proxy_set_header X-Real-IP $remote_addr;
                        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                        proxy_set_header X-Forwarded-Proto $scheme;
                    }}
                    
                    location /health {{
                        access_log off;
                        return 200 "Loadbalancer healthy\\n";
                    }}
                }}
            }}
        """))
        
def generate_api_gateway(name, backends):
    path = f'skeleton/{name}'
    os.makedirs(path, exist_ok=True)

    with open(os.path.join(path, 'app.py'), 'w') as f:
        f.write(textwrap.dedent(f"""
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
            SERVICE_REGISTRY = {{
                'systems': ['ecommerce_be_or', 'ecommerce_be_pd', 'ecommerce_be_inv'],
                'create': ['ecommerce_be_or'], 
                'process': ['ecommerce_be_pmt']
            }}

            # Define direct service routes
            SERVICE_ROUTES = {{
                'ecommerce_be_or': 'http://ecommerce_be_or:80',
                'ecommerce_be_pd': 'http://ecommerce_be_pd:80',
                'ecommerce_be_inv': 'http://ecommerce_be_inv:80',
                'ecommerce_be_pmt': 'http://ecommerce_be_pmt:80'
            }}

            # Select service using simple round-robin load balancing
            def get_service_for_endpoint(endpoint):
                services = SERVICE_REGISTRY.get(endpoint)
                if not services:
                    return None
                return random.choice(services)

            # Generic route handler for proxying requests
            async def proxy_request(target_service, request: Request, path: str):
                method = request.method
                target_url = f"{{SERVICE_ROUTES[target_service]}}/{{path}}"
                
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
                        raise HTTPException(status_code=503, detail=f"Service unavailable: {{str(e)}}")

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
           @app.api_route("/{{service}}/{{path:path}}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
            async def service_routes(service: str, path: str, request: Request):
                if service not in SERVICE_ROUTES:
                    raise HTTPException(status_code=404, detail=f"Service '{{service}}' not found")
                return await proxy_request(service, request, path)

            @app.get("/health")
            async def health_check():
                return {{"status": "API Gateway is healthy"}}

            if __name__ == "__main__":
                uvicorn.run("app:app", host="0.0.0.0", port=80, reload=True)
            """
        ))

    with open(os.path.join(path, 'Dockerfile'), 'w') as f:
        f.write(textwrap.dedent("""
            FROM python:3.11-slim
            
            WORKDIR /app
            COPY . .
            
            RUN pip install fastapi uvicorn httpx
            
            CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80"]
            """
        ))

    # Add requirements.txt for clarity
    with open(os.path.join(path, 'requirements.txt'), 'w') as f:
        f.write(textwrap.dedent("""
            fastapi==0.104.1
            uvicorn==0.23.2
            httpx==0.25.1
            """
        ))

def generate_docker_compose(components):
    path = f'skeleton/'
    os.makedirs(path, exist_ok=True)

    with open(os.path.join(path, 'docker-compose.yml'), 'w') as f:
        # Order components by type for proper dependency management
        sorted_components = {}
        for name, ctype in components.items():
            if ctype not in sorted_components:
                sorted_components[ctype] = []
            sorted_components[ctype].append(name)
        
        f.write("version: '3.8'\n\nservices:\n")
        
        # Add RabbitMQ if we have a mqtp component
        if "mqtp" in sorted_components:
            f.write("  rabbitmq:\n")
            f.write("    image: rabbitmq:3-management\n")
            f.write("    ports:\n")
            f.write("      - '5672:5672'\n")
            f.write("      - '15672:15672'\n")
            f.write("    environment:\n")
            f.write("      - RABBITMQ_DEFAULT_USER=guest\n")
            f.write("      - RABBITMQ_DEFAULT_PASS=guest\n")
            f.write("    healthcheck:\n")
            f.write("      test: rabbitmq-diagnostics -q ping\n")
            f.write("      interval: 30s\n")
            f.write("      timeout: 10s\n")
            f.write("      retries: 5\n\n")

        # Databases first
        if "database" in sorted_components:
            for name in sorted_components["database"]:
                f.write(f"  {name}:\n")
                f.write("    image: mysql:8\n")
                f.write("    environment:\n")
                f.write("      - MYSQL_ROOT_PASSWORD=root\n")
                f.write(f"      - MYSQL_DATABASE={name}\n")
                f.write("    volumes:\n")
                f.write(f"      - ./{name}/init.sql:/docker-entrypoint-initdb.d/init.sql\n")
                f.write("    healthcheck:\n")
                f.write("      test: mysqladmin ping -h localhost -proot\n")
                f.write("      interval: 30s\n")
                f.write("      timeout: 10s\n")
                f.write("      retries: 5\n\n")

        # Backends
        backend_services = []
        if "backend" in sorted_components:
            for name in sorted_components["backend"]:
                backend_services.append(name)
                f.write(f"  {name}:\n")
                f.write(f"    build: ./{name}\n")
                f.write("    depends_on:\n")
                # Find database connections
                for db_name in sorted_components.get("database", []):
                    if db_name.startswith(name):
                        f.write(f"      {db_name}:\n")
                        f.write("        condition: service_healthy\n")
                f.write("    healthcheck:\n")
                f.write("      test: wget --no-verbose --tries=1 --spider http://localhost:80/health || exit 1\n")
                f.write("      interval: 30s\n")
                f.write("      timeout: 10s\n")
                f.write("      retries: 5\n\n")

        # Message Queue Based Services
        mqtp_services = []
        if "mqtp" in sorted_components:
            for name in sorted_components["mqtp"]:
                mqtp_services.append(name)
                f.write(f"  {name}:\n")
                f.write(f"    build: ./{name}\n")
                f.write("    depends_on:\n")
                f.write("      rabbitmq:\n")
                f.write("        condition: service_healthy\n")
                # Find database connections
                for db_name in sorted_components.get("database", []):
                    if db_name.startswith(name):
                        f.write(f"      {db_name}:\n")
                        f.write("        condition: service_healthy\n")
                f.write("    healthcheck:\n")
                f.write("      test: wget --no-verbose --tries=1 --spider http://localhost:80/health || exit 1\n")
                f.write("      interval: 30s\n")
                f.write("      timeout: 10s\n")
                f.write("      retries: 5\n\n")

        # API Gateway
        api_gateway_name = None
        if "api_gateway" in sorted_components:
            api_gateway_name = sorted_components["api_gateway"][0]
            f.write(f"  {api_gateway_name}:\n")
            f.write(f"    build: ./{api_gateway_name}\n")
            f.write("    depends_on:\n")
            for service in backend_services + mqtp_services:
                f.write(f"      {service}:\n")
                f.write("        condition: service_healthy\n")
            f.write("    healthcheck:\n")
            f.write("      test: wget --no-verbose --tries=1 --spider http://localhost:80/health || exit 1\n")
            f.write("      interval: 30s\n")
            f.write("      timeout: 10s\n")
            f.write("      retries: 5\n\n")

        # Frontend
        frontend_name = None
        if "frontend" in sorted_components:
            frontend_name = sorted_components["frontend"][0]
            f.write(f"  {frontend_name}:\n")
            f.write(f"    build: ./{frontend_name}\n")
            f.write("    depends_on:\n")
            f.write(f"      {api_gateway_name}:\n")
            f.write("        condition: service_healthy\n")
            f.write("    healthcheck:\n")
            f.write("      test: wget --no-verbose --tries=1 --spider http://localhost:80/health || exit 1\n")
            f.write("      interval: 30s\n")
            f.write("      timeout: 10s\n")
            f.write("      retries: 5\n\n")

        # Load Balancer
        if "load_balancer" in sorted_components:
            load_balancer_name = sorted_components["load_balancer"][0]
            f.write(f"  {load_balancer_name}:\n")
            f.write(f"    build: ./{load_balancer_name}\n")
            f.write("    ports:\n")
            f.write("      - '8080:80'\n")
            f.write("    depends_on:\n")
            f.write(f"      {frontend_name}:\n")
            f.write("        condition: service_healthy\n\n")

        f.write("\nnetworks:\n  default:\n    driver: bridge\n")


def apply_transformations(model):

    components = {}
    connectors = {}
    api_gateway_name = None
    backend_name = None
    database_name = None
    frontend_name = None

    for e in model.elements:
        if e.__class__.__name__ == 'Component':
            components[e.name] = e.type
            if e.type == 'api_gateway':
                api_gateway_name = e.name
            elif e.type == 'frontend':
                frontend_name = e.name

     
    backend_components = {}
    for name, ctype in components.items():
        if ctype == 'database':
            generate_database(name)
        elif ctype == 'backend':
            db_name = None
            if name in connectors:
                for conn in connectors[name]:
                    if components[conn['to']] == 'database' and conn['type'] == 'db_connector':
                        db_name = conn['to']
                        break
            generate_backend(name, database=db_name)
            backend_components[name] = ctype
        elif ctype == 'mqtp':
            db_name = None
            if name in connectors:
                for conn in connectors[name]:
                    if components[conn['to']] == 'database' and conn['type'] == 'db_connector':
                        db_name = conn['to']
                        break
            generate_mqtp(name, database=db_name)
            backend_components[name] = ctype
        elif ctype == 'frontend':
            generate_frontend(name, api_gateway=api_gateway_name)
        elif ctype == 'api_gateway':
            generate_api_gateway(name, backend_components)
        elif ctype == 'load_balancer':
            generate_load_balancer(name, frontend_name=frontend_name)

    generate_docker_compose(components)