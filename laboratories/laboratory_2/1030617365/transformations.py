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
            import socket 

            app = Flask(__name__)

            @app.route('/create', methods=['POST'])
            def create():
                try:
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
                except Exception as e:
                    return jsonify(error=str(e), 500

            @app.route('/systems')
            def get_systems():
                try:
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
                except Exception as e:
                    return jsonify(error=str(e), 500

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

def generate_frontend(name, load_balancer):
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
                                
            const LOAD_BALANCER_URL = 'http://{load_balancer}:80';

            app.get('/', async (req, res) => {{
            try {{
                const response = await axios.get(`${{LOAD_BALANCER_URL}}/systems`);
                const systems = response.data.systems;
                let list = systems.map(([id, name]) => `<li>${{name}} </li>`).join('');
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
                await axios.post(`${{LOAD_BALANCER_URL}}/create`, {{ name }});
                res.redirect('/');
            }});
            app.listen(80, () => console.log("Frontend running on port 80"));
            """
        ))

def generate_load_balancer(name, backend_name):
    path = f'skeleton/{name}'
    os.makedirs(path, exist_ok=True)

    # Crear configuración de Nginx
    with open(os.path.join(path, 'nginx.conf'), 'w') as f:
        f.write(textwrap.dedent(f"""
            events {{
                worker_connections 1024;
            }}

            http {{
                upstream backend {{
                    server {backend_name}:80;
                }}

                server {{
                    listen 80;
                    
                    location / {{
                        proxy_pass http://backend;
                        proxy_set_header Host $host;
                        proxy_set_header X-Real-IP $remote_addr;
                        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                        proxy_set_header X-Forwarded-Proto $scheme;
                        proxy_read_timeout 300;
                        proxy_connect_timeout 300;
                        proxy_http_version 1.1;
                        proxy_set_header Upgrade $http_upgrade;
                        proxy_set_header Connection 'upgrade';
                    }}
                }}
            }}
            """
        ))

    # Crear Dockerfile para el balanceador
    with open(os.path.join(path, 'Dockerfile'), 'w') as f:
        f.write(textwrap.dedent("""
            FROM nginx:latest
            COPY nginx.conf /etc/nginx/nginx.conf
            RUN mkdir -p /var/log/nginx
            RUN touch /var/log/nginx/error.log /var/log/nginx/access.log
            EXPOSE 80
            """
        ))



def generate_docker_compose(components):
    path = f'skeleton/'
    os.makedirs(path, exist_ok=True)

    with open(os.path.join(path, 'docker-compose.yml'), 'w') as f:
        sorted_components = dict(sorted(components.items(), key=lambda
        item: {
            "database": 0,
            "backend": 1,
            "load_balancer": 2,
            "frontend": 3
        }.get(item[1], 4)))

        f.write("version: '3'\n\n")
        f.write("services:\n")

        db = None
        backend = None
        load_balancer = None

        for i, (name, ctype) in enumerate(sorted_components.items()):
            port = 8000 + i
            f.write(f" {name}:\n")
            if ctype == "database":
                db = name
                f.write("    image: mysql:8\n")
                f.write("    environment:\n")
                f.write("      MYSQL_ROOT_PASSWORD: root\n")  # Corregimos el formato
                f.write(f"      MYSQL_DATABASE: {name}\n")
                f.write("    volumes:\n")
                f.write(f"      - ./{name}/init.sql:/docker-entrypoint-initdb.d/init.sql\n")
                f.write("    ports:\n")
                f.write("      - '3306:3306'\n")
            elif ctype == "backend":
                backend = name
                f.write("    build:\n")  # Corregimos el formato del build
                f.write(f"      context: ./{name}\n")
                f.write("    ports:\n")
                f.write(f"      - '{port}:80'\n")
                if db:
                    f.write("    depends_on:\n")
                    f.write(f"      - {db}\n")
            
            elif ctype == "load_balancer":
                load_balancer = name
                f.write("    build:\n")
                f.write(f"      context: ./{name}\n")
                f.write("    ports:\n")
                f.write(f"      - '{port}:80'\n")
                if backend:
                    f.write("    depends_on:\n")
                    f.write(f"      - {backend}\n")
            
            elif ctype == "frontend":
                f.write("    build:\n")
                f.write(f"      context: ./{name}\n")
                f.write("    ports:\n")
                f.write(f"      - '{port}:80'\n")
                if load_balancer:
                    f.write("    depends_on:\n")
                    f.write(f"      - {load_balancer}\n")
        
        f.write("\nnetworks:\n  default:\n    driver: bridge\n")

def apply_transformations(model):
    components = {}
    backend_name = None
    database_name = None
    load_balancer_name = None

    # Primera pasada para identificar componentes
    for e in model.elements:
        if e.__class__.__name__ == 'Component':
            if e.type == 'backend':
                backend_name = e.name
            elif e.type == 'database':
                database_name = e.name
            elif e.type == 'load_balancer':
                load_balancer_name = e.name
    
    # Segunda pasada para generar componentes
    for e in model.elements:
        if e.__class__.__name__ == 'Component':
            components[e.name] = e.type
            if e.type == 'database':
                generate_database(e.name)
            elif e.type == 'backend':
                generate_backend(e.name, database=database_name)
            elif e.type == 'load_balancer':
                generate_load_balancer(e.name, backend_name)
            elif e.type == 'frontend':
                generate_frontend(e.name, load_balancer=load_balancer_name)

    generate_docker_compose(components)

