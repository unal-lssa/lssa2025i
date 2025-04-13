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

            app.get('/health', async (req, res) => {{
                res.status(200).send("Healthcheck OK!");
            }});

            app.listen(80, () => console.log("Frontend running on port 80"));
            """
        ))

def generate_load_balancer(name, frontend):
    
    path = f'skeleton/{name}'
    os.makedirs(path, exist_ok=True)

    with open(os.path.join(path, 'Dockerfile'), 'w') as f:
        f.write(textwrap.dedent("""
            FROM haproxy:2.8-alpine

            COPY haproxy.cfg /usr/local/etc/haproxy/haproxy.cfg

            EXPOSE 80 8404

            # Health check
            HEALTHCHECK --interval=5s --timeout=3s CMD wget --no-verbose --tries=1 --spider http://localhost:8404/stats || exit 1
            """
        ))

    with open(os.path.join(path, 'haproxy.cfg'), 'w') as f:
        f.write(textwrap.dedent(f"""
            global
                log stdout format raw local0
                maxconn 4096
                user haproxy
                group haproxy

            defaults
                log     global
                mode    http
                option  httplog
                option  dontlognull
                retries 3
                timeout connect 5s
                timeout client  30s
                timeout server  30s
                timeout http-request 10s

            # Stats page
            listen stats
                bind *:8404
                stats enable
                stats uri /stats
                stats refresh 10s
                stats admin if TRUE

            # Frontend configuration
            frontend http_front
                bind *:80
                default_backend web_servers
                
                # Add request headers
                http-request set-header X-Forwarded-Proto http

            # Backend configuration for web servers
            backend web_servers
                balance roundrobin
                option httpchk GET /health
                http-check expect status 200
                server {frontend} {frontend}:80 check
            """
        ))

def generate_docker_compose(components):

    path = f'skeleton/'
    os.makedirs(path, exist_ok=True)

    with open(os.path.join(path, 'docker-compose.yml'), 'w') as f:
        
        sorted_components = dict(sorted(components.items(), key=lambda item: 0 if item[1] == "database" else 1))

        f.write("services:\n")

        db = None
        fe = None

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
            else:
                f.write(f"    build: ./{name}\n")
                f.write(f"    ports:\n      - '{port}:80'\n")
                if ctype== "backend":
                    f.write(f"    depends_on:\n      - {db}\n")
                if ctype== "frontend":
                    fe = name
                if ctype== "load_balancer":
                    f.write(f"    ports:\n      - '8084:8084'\n")
                    f.write(f"    depends_on:\n      - {fe}\n")
                    f.write(f"    restart: unless-stoped\n")

        f.write("\nnetworks:\n  default:\n    driver: bridge\n")


def apply_transformations(model):

    components = {}
    backend_name = None
    database_name = None
    frontend_name = None

    for e in model.elements:
        if e.__class__.__name__ == 'Component':
            if e.type == 'backend':
                backend_name = e.name
            elif e.type == 'frontend':
                frontend_name = e.name
            elif e.type == 'database':
                database_name = e.name

    for e in model.elements:
        if e.__class__.__name__ == 'Component':
            components[e.name] = e.type
            if e.type == 'database':
                generate_database(e.name)
            if e.type == 'backend':
                generate_backend(e.name, database=database_name)
            elif e.type == 'frontend':
                generate_frontend(e.name, frontend=backend_name)
            elif e.type == 'load_balancer':
                generate_load_balancer(e.name, frontend=frontend_name)

    generate_docker_compose(components)