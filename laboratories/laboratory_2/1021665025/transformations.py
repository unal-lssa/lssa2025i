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

def generate_load_balancer(name, backend_servers):
    path = f'skeleton/{name}'
    os.makedirs(path, exist_ok=True)

    # Generate nginx.conf
    upstream_servers = "\n        ".join([f"server {server}:80;" for server in backend_servers])
    nginx_config = textwrap.dedent(f"""
        upstream backend {{
            # Using Round Robin algorithm for load balancing
            {upstream_servers}
        }}

        server {{
            listen 80;
            server_name localhost;

            location / {{
                proxy_pass http://backend;
                proxy_set_header Host $host;
                proxy_set_header X-Real-IP $remote_addr;
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                proxy_set_header X-Forwarded-Proto $scheme;
            }}
        }}
    """)
    with open(os.path.join(path, 'nginx.conf'), 'w') as f:
        f.write(nginx_config)

    # Generate Dockerfile
    dockerfile_content = textwrap.dedent("""
        FROM nginx:latest
        COPY nginx.conf /etc/nginx/conf.d/default.conf
        EXPOSE 80
    """)
    with open(os.path.join(path, 'Dockerfile'), 'w') as f:
        f.write(dockerfile_content)


def generate_docker_compose(components):
    path = f'skeleton/'
    os.makedirs(path, exist_ok=True)
    sorted_components = dict(sorted(components.items(), key=lambda item: 0 if item[1] == "database" else 1 if item[1] == "frontend" else 2 if item[1] == "load_balancer" else 3))
    with open(os.path.join(path, 'docker-compose.yml'), 'w') as f:
        f.write("services:\n")
        db = None
        lb = None
        for i, (name, ctype) in enumerate(sorted_components.items()):
            port = 8000 + i
            f.write(f"  {name}:\n")
            if ctype == "database":
                db = name
                f.write("    image: mysql:8\n")
                f.write("    environment:\n")
                f.write("      - MYSQL_ROOT_PASSWORD=root\n")
                f.write(f"      - MYSQL_DATABASE={name}\n")
                f.write("    volumes:\n")
                f.write(f"      - ./{name}/init.sql:/docker-entrypoint-initdb.d/init.sql\n")
                f.write("    ports:\n")
                f.write("      - '3306:3306'\n")
            elif ctype == "load_balancer":
                lb = name
                f.write(f"    build: ./{name}\n")
                f.write("    ports:\n")
                f.write(f"      - '{port}:80'\n")
                f.write("    depends_on:\n")
                for backend in [comp_name for comp_name, comp_type in components.items() if comp_type == 'backend']:
                    f.write(f"      - {backend}\n")
                f.write("    command: sh -c \"sleep 5 && nginx -g 'daemon off;'\"\n")
            elif ctype == "frontend":
                f.write(f"    build: ./{name}\n")
                f.write(f"    ports:\n    - '{port}:80'\n")
                if lb:
                    f.write(f"    depends_on:\n      - {lb}\n")
            elif ctype == "backend":
                f.write(f"    build: ./{name}\n")
                f.write(f"    ports:\n    - '{port}:80'\n")
                if db:
                    f.write(f"    depends_on:\n      - {db}\n")

        f.write("\nnetworks:\n  default:\n    driver: bridge\n")

def apply_transformations(model):
    components = {}
    backend_servers = []
    load_balancer_name = None
    database_name = None

    for e in model.elements:
        if e.__class__.__name__ == 'Component':
            components[e.name] = e.type
            if e.type == 'backend':
                backend_servers.append(e.name)
            elif e.type == 'load_balancer':
                load_balancer_name = e.name
            elif e.type == 'database':
                database_name = e.name

    for e in model.elements:
        if e.__class__.__name__ == 'Component':
            if e.type == 'database':
                generate_database(e.name)
            elif e.type == 'backend':
                generate_backend(e.name, database=database_name)
            elif e.type == 'frontend':
                # Assuming only one load balancer, using its name
                generate_frontend(e.name, backend=load_balancer_name)
            elif e.type == 'load_balancer':
                generate_load_balancer(e.name, backend_servers)

    generate_docker_compose(components)
