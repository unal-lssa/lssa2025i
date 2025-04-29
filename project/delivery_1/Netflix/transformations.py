import os
import yaml
from generators import generate_react_project_structure 

architecture = {
    "frontend": [
        {"name": "web_frontend", "port": 80, "category":"frontend"}
    ],
    "services": [
        {"name": "ms_streamer", "port": 8001},
        {"name": "ms_recommender", "port": 8002},
        {"name": "ms_auth", "port": 8003},
        {"name": "ms_accounts", "port": 8004},
        {"name": "ms_payment", "port": 8005},
        {"name": "ms_content", "port": 8006},
    ],
    "loadbalancers": [
        {"name": "streamer_lb", "port": 443}
    ],
    "storage": [
        {"name": "media_storage", "size": "500gb"}
    ],
    "databases": [
        {"type": "mongo", "name": "recommender_db"},
        {"type": "mongo", "name": "payment_db"},
        {"type": "mongo", "name": "auth_db"},
        {"type": "mysql", "name": "accounts_db"},
        {"type": "mongo", "name": "content_db"},
    ],
    "caches": [
        {"type": "redis", "name": "content_cache", "size": "1gb"}
    ],
    "event_streams": [
        {"type": "kafka", "name": "kafka_service", "partitions": 3}
    ]
}



def generate_service_code(component):
    port = component.get("port", '') 
    return f"""# {component['name']} Service
from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return "Hello from {component['name']}!"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port={port})
"""

def generate_loadbalancer_code(component):
    return f"""# {component['name']} Load Balancer Config
server {{
    listen {component['port']};
    server_name {component['name']};
}}
"""

def generate_storage_code(component):
    return f"""# {component['name']} Storage Configuration
storage_name: {component['name']}
"""

def generate_database_code(component):
    return f"""# {component['name']} Database
category: {component['category']}
"""

def generate_cache_code(component):
    return f"""# {component['name']} Cache
category: {component['category']}
"""

def generate_event_stream_code(component):
    return f"""# {component['name']} Event Stream
category: {component['category']}
"""

generators = {
    "frontend": generate_react_project_structure,
    "services": generate_service_code,
    "loadbalancers": generate_loadbalancer_code,
    "storage": generate_storage_code,
    "databases": generate_database_code,
    "caches": generate_cache_code,
    "event_streams": generate_event_stream_code
}

def generate_dockerfile(category, component):
    dockerfile = ""

    if category in ["frontend", "mobile_client"]:
        dockerfile = f"""
FROM node:20-alpine
WORKDIR /app
COPY . .
RUN npm install
RUN npm run build
EXPOSE {component.get("port", "80")}
CMD ["npm", "start"]
"""

    elif category in ["backend", "auth_service", "payment_service", "streaming_service", "recommendation_service", "content_service", "account_service", "services"]:
        dockerfile = f"""
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install flask 
EXPOSE {component.get("port", "8000")}
CMD ["python", "app.py"]
"""

    elif category in ["loadbalancer"]:
        dockerfile = f"""
FROM nginx:stable-alpine
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE {component.get("port", "443")}
CMD ["nginx", "-g", "daemon off;"]
"""

    elif category in ["storage"]:
        dockerfile = """
FROM minio/minio
EXPOSE 9000
CMD ["server", "/data"]
"""

    elif category in ["cache"]:
        dockerfile = """
FROM redis:7-alpine
EXPOSE 6379
"""

    elif category in ["database"]:
        dockerfile = """
FROM mongo:7
EXPOSE 27017
"""

    else:
        dockerfile = f"""
FROM alpine
CMD ["echo", "Componente {component['name']} de tipo {category}"]
"""

    return dockerfile.strip()

def generate_docker_compose(architecture):
    services = {}

    for category in ["frontend", "services", "components"]:
        for component in architecture.get(category, []):
            service = {
                "build": f"./{component['name']}",
                "restart": "always"
            }
            if "port" in component:
                service["ports"] = [f"{component['port']}:{component['port']}"]
            services[component["name"]] = service
    
    for db in architecture.get("databases", []):
        port = {
            "mongo": "27017",
            "mysql": "3306"
        }.get(db["category"], "0000")
        
        services[db["name"]] = {
            "image": f'{db["category"]}:latest',
            "ports": [f"{port}:{port}"],
            "restart": "always",
        }

    for cache in architecture.get("caches", []):
        services[cache["name"]] = {
            "image": f"{cache['category']}:latest",
            "ports": ["6379:6379"],
            "restart": "always"
        }

    for stream in architecture.get("event_streams", []):
        services[stream["name"]] = {
            "image": "apache/kafka",
            "ports": ["9092:9092"],
            "restart": "always",
            "environment": {
                "KAFKA_PARTITIONS": str(stream["partitions"])
            }
        }

    compose = {
        "services": services
    }

    os.makedirs("skeleton", exist_ok=True)
    with open("skeleton/docker-compose.yml", "w") as f:
        yaml.dump(compose, f, sort_keys=False, default_flow_style=False)

def apply_transformations(architecture):
    os.makedirs('skeleton', exist_ok=True)
    
    for category, components in architecture.items():
        for component in components:
            folder = f"skeleton/{component['name']}"
            os.makedirs(folder, exist_ok=True)
            print("category",category)
            
            if category == "frontend":
                filename = "app.js"
            elif category == "services":
                filename = "app.py"
            elif category == "components":
                filename = "app.py"
            elif category == "loadbalancers":
                filename = "nginx.conf"
            elif category == "storage":
                filename = "storage.yaml"
            elif category == "databases":
                filename = "database.yaml"
            elif category == "caches":
                filename = "cache.yaml"
            elif category == "event_streams":
                filename = "eventstream.yaml"
            else:
                filename = "config.txt"

            main_path = os.path.join(folder, filename)

            generator = generators.get(category)
            print("generator",generate_service_code(component))
            if generator:
                body = generator(component)
            else:
                body = f"# {component['name']} configuration"

            with open(main_path, "w") as f:
                f.write(body)

            if category in ["frontend", "services","components"]:
                dockerfile_path = os.path.join(folder, "Dockerfile")
                dockerfile_content = generate_dockerfile(category, component)
                with open(dockerfile_path, "w") as f:
                    f.write(dockerfile_content)

            if category == "loadbalancers":
                dockerfile_path = os.path.join(folder, "Dockerfile")
                dockerfile_content = generate_nginx_dockerfile(component)
                with open(dockerfile_path, "w") as f:
                    f.write(dockerfile_content)


    generate_docker_compose(architecture)
