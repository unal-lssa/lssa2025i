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


def generate_frontend(name, backend):
    
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

            const BACKEND_URL = 'http://{backend}:80';

            app.get('/', async (req, res) => {{
            try {{
                const response = await axios.get(`${{BACKEND_URL}}/systems`);
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
                res.status(500).send("Error contacting backend");
            }}
            }});

            app.post('/create', async (req, res) => {{
            const name = req.body.name;
            await axios.post(`${{BACKEND_URL}}/create`, {{ name }});
            res.redirect('/');
            }});

            app.listen(80, () => console.log("Frontend running on port 80"));
            """
        ))

def generate_docker_compose(components, replicas=None, load_balancer_config=None):
    path = f'skeleton/'
    os.makedirs(path, exist_ok=True)
    
    if replicas is None:
        replicas = {}
    
    if load_balancer_config is None:
        load_balancer_config = {}

    with open(os.path.join(path, 'docker-compose.yml'), 'w') as f:
        sorted_components = dict(sorted(components.items(), key=lambda item: 0 if item[1] == "database" else 1))
        f.write("services:\n")

        db = None
        port_counter = 8001
        
        for name, ctype in sorted_components.items():
            if ctype == "database":
                db = name
                f.write(f"  {name}:\n")
                f.write("    image: mysql:8\n")
                f.write("    environment:\n")
                f.write("      - MYSQL_ROOT_PASSWORD=root\n")
                f.write(f"      - MYSQL_DATABASE={name}\n")
                f.write("    volumes:\n")
                f.write(f"      - ./{name}/init.sql:/docker-entrypoint-initdb.d/init.sql\n")
                f.write("    ports:\n")
                f.write("      - '3306:3306'\n")
        
        for name, ctype in sorted_components.items():
            if ctype == "database":
                continue
                
            # Check if the component has replicas defined
            replica_count = replicas.get(name, 1)
            
            # Check if the component is a target of a load balancer
            is_balanced = name in load_balancer_config.values()
            
            # Create replicas if applicable
            if replica_count > 1 or is_balanced:
                for i in range(replica_count):
                    instance_name = f"{name}_{i}"
                    f.write(f"  {instance_name}:\n")
                    f.write(f"    build: ./{name}\n")
                    
                    if ctype == "backend" and db:
                        f.write("    depends_on:\n")
                        f.write(f"      - {db}\n")
                    elif ctype == "frontend":
                        backend_service = None
                        for lb_name, target_name in load_balancer_config.items():
                            backend_service = lb_name
                            break
                        
                        if not backend_service:
                            for comp_name, comp_type in components.items():
                                if comp_type == "backend":
                                    if comp_name in replicas and replicas[comp_name] > 1:
                                        backend_service = f"{comp_name}_0"
                                    else:
                                        backend_service = comp_name
                                    break
                        
                        if backend_service:
                            f.write("    depends_on:\n")
                            f.write(f"      - {backend_service}\n")
                    
                    if i == 0 and not is_balanced:
                        f.write("    ports:\n")
                        f.write(f"      - '{port_counter}:80'\n")
                        port_counter += 1
            else:
                f.write(f"  {name}:\n")
                f.write(f"    build: ./{name}\n")
                
                if ctype == "backend" and db:
                    f.write("    depends_on:\n")
                    f.write(f"      - {db}\n")
                elif ctype == "frontend":
                    backend_service = None
                    for lb_name, target_name in load_balancer_config.items():
                        backend_service = lb_name
                        break
                    
                    if not backend_service:
                        for comp_name, comp_type in components.items():
                            if comp_type == "backend":
                                if comp_name in replicas and replicas[comp_name] > 1:
                                    backend_service = f"{comp_name}_0"
                                else:
                                    backend_service = comp_name
                                break
                    
                    if backend_service:
                        f.write("    depends_on:\n")
                        f.write(f"      - {backend_service}\n")
                
                f.write("    ports:\n")
                f.write(f"      - '{port_counter}:80'\n")
                port_counter += 1
                
            if ctype == "loadbalancer":
                target_name = load_balancer_config.get(name)
                if target_name:
                    target_replicas = replicas.get(target_name, 1)
                    f.write("    depends_on:\n")
                    for i in range(target_replicas):
                        f.write(f"      - {target_name}_{i}\n")

def generate_loadbalancer(name, service_name, instance_count):
    path = f'skeleton/{name}'
    os.makedirs(path, exist_ok=True)

    upstream_block = '\n'.join([f"        server {service_name}_{i}:80;" for i in range(instance_count)])

    nginx_conf = textwrap.dedent(f"""
        events {{}}

        http {{
            upstream servers {{
{upstream_block}
            }}

            server {{
                listen 80;

                location / {{
                    proxy_pass http://servers;
                    proxy_set_header Host $host;
                    proxy_set_header X-Real-IP $remote_addr;
                    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                    proxy_set_header X-Forwarded-Proto $scheme;
                }}
            }}
        }}
    """)

    with open(os.path.join(path, 'nginx.conf'), 'w') as f:
        f.write(nginx_conf)

    with open(os.path.join(path, 'Dockerfile'), 'w') as f:
        f.write(textwrap.dedent("""
            FROM nginx:alpine
            COPY nginx.conf /etc/nginx/nginx.conf
            
            EXPOSE 80
            
            CMD ["nginx", "-g", "daemon off;"]
        """))

def apply_transformations(model):
    components = {}
    replicas = {}
    load_balancer_config = {}
    database_name = None

    for e in model.elements:
        if e.__class__.__name__ == 'Component' or e.__class__.__name__ == 'StandardComponent':
            components[e.name] = e.type
            
            if e.type == 'database':
                database_name = e.name
                
            if hasattr(e, 'instances') and e.instances is not None:
                replicas[e.name] = e.instances.count
        
        elif e.__class__.__name__ == 'LoadBalancer':
            load_balancer_name = e.name
            components[load_balancer_name] = 'loadbalancer'
            
            if hasattr(e, 'target') and e.target is not None:
                target_name = e.target.name
                load_balancer_config[load_balancer_name] = target_name
                
                if target_name not in replicas and hasattr(e, 'instanceCount'):
                    replicas[target_name] = e.instanceCount

    for e in model.elements:
        if e.__class__.__name__ == 'Component' or e.__class__.__name__ == 'StandardComponent':
            if e.type == 'database':
                generate_database(e.name)
            elif e.type == 'backend':
                generate_backend(e.name, database=database_name)
            elif e.type == 'frontend':
                # Connect frontend to load balancer if it exists, otherwise connect to backend
                backend_service = None
                target_name = None
                for lb_name, target_name in load_balancer_config.items():
                    backend_service = lb_name
                    break
                generate_frontend(e.name, backend=backend_service if backend_service else target_name)

        elif e.__class__.__name__ == 'LoadBalancer':
            target_name = load_balancer_config.get(e.name)
            if target_name:
                replica_count = replicas.get(target_name, 1)
                generate_loadbalancer(e.name, target_name, replica_count)

    generate_docker_compose(components, replicas, load_balancer_config)
