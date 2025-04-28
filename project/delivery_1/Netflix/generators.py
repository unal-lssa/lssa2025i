import yaml

def generate_react_project_structure(component):
    return """import React from 'react';

function App() {
  return (
    <div>
      <h1>Hello from React Frontend!</h1>
    </div>
  );
}

export default App;
"""


def generate_dockerfile(category, component):
    name = component["name"]

    if category == "frontend":
        dockerfile = f"""
# Use Node.js for build
FROM node:18 AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Serve with Nginx
FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
"""
    elif category == "services":
        dockerfile = f"""
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE {component.get('port', 8000)}
CMD ["python", "app.py"]
"""
    else:
        raise ValueError(f"Categoría no soportada: {category}")

    return dockerfile.strip()


def generate_nginx_dockerfile(component):
    return f"""
FROM nginx:stable-alpine
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE {component.get("port", 443)}
CMD ["nginx", "-g", "daemon off;"]
""".strip()


import os
import yaml

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
            "mongodb": "27017",
            "mysql": "3306"
        }.get(db["type"], "0000")
        
        services[db["name"]] = {
            "image": f"{db['type']}:latest",
            "ports": [f"{port}:{port}"],
            "restart": "always",
        }

    for cache in architecture.get("caches", []):
        services[cache["name"]] = {
            "image": f"{cache['type']}:latest",
            "ports": ["6379:6379"],
            "restart": "always"
        }

    for stream in architecture.get("event_streams", []):
        services[stream["name"]] = {
            "image": "bitnami/kafka:latest",
            "ports": ["9092:9092"],
            "restart": "always",
            "environment": {
                "KAFKA_PARTITIONS": str(stream["partitions"])
            }
        }

    compose = {
        "version": "3",
        "services": services
    }

    os.makedirs("skeleton", exist_ok=True)
    with open("skeleton/docker-compose.yml", "w") as f:
        yaml.dump(compose, f, sort_keys=False, default_flow_style=False)