# Laboratorio 2 - Modelado de Arquitectura de Software con MDE

**Nombre completo**: Juan David Ramírez Ávila


**Asignatura**: Arquitectura de Software a Gran Escala


**Fecha de entrega**: 12 de abril de 2025

---

## 📌 Objetivo  
Este laboratorio tiene como objetivo aplicar el paradigma de **Ingeniería de Software Dirigida por Modelos (MDE)** para automatizar la generación del esqueleto de un sistema software desde una perspectiva arquitectónica. Se utilizará un DSL (*Domain-Specific Language*) para definir metamodelos, transformaciones y generar código automáticamente.

## Modificaciones a los archivos arch.tx, transformations.py y model.arch

Se modifica el archivo arch.tx para incluir el balanceador de carga, como se ilustra seguidamente 

```ebnf
Model: 
    'architecture' ':' 
        elements*=Element 
; 
 
Element: 
    Component | Connector 
; 
 
Component: 
    'component' type=ComponentType name=ID 
; 
 
Connector: 
    'connector' type=ConnectorType from=[Component] '->' to=[Component] 
; 
 
ComponentType: 
    'frontend' | 'backend' | 'database' | 'load_balancer' 
; 
 
ConnectorType: 
    'http' | 'db_connector'  
; 
```

Se modifica el archivo transformations.py, con el objetivo de incluir el balanceador de carga, se agrego la transformación generate_load_balancer, como se aprecia a continuación: 

```ebnf
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
        """))

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
        """))
    with open(os.path.join(path, 'Dockerfile'), 'w') as f:
        f.write(textwrap.dedent("""
            FROM python:3.11-slim
            WORKDIR /app
            COPY . .
            RUN pip install flask mysql-connector-python
            CMD ["python", "app.py"]
        """))

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
        """))
    with open(os.path.join(path, 'Dockerfile'), 'w') as f:
        f.write(textwrap.dedent("""
            FROM node:18
            WORKDIR /app
            COPY . .
            RUN npm install
            CMD ["node", "app.js"]
        """))

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
        """))

def generate_load_balancer(name, backend):
    path = f'skeleton/{name}'
    os.makedirs(path, exist_ok=True)
    with open(os.path.join(path, 'package.json'), 'w') as f:
        f.write(textwrap.dedent("""
            {
                "name": "load-balancer",
                "version": "1.0.0",
                "main": "server.js",
                "dependencies": {
                    "express": "^4.18.2",
                    "http-proxy-middleware": "^2.0.6"
                }
            }
        """))
    with open(os.path.join(path, 'server.js'), 'w') as f:
        f.write(textwrap.dedent(f"""
            const express = require('express');
            const {{ createProxyMiddleware }} = require('http-proxy-middleware');
            const app = express();

            const BACKEND = 'http://{backend}:80';

            app.use('/', createProxyMiddleware({{
                target: BACKEND,
                changeOrigin: true
            }}));

            app.listen(80, () => {{
                console.log('Load Balancer running on port 80');
            }});
        """))
    with open(os.path.join(path, 'Dockerfile'), 'w') as f:
        f.write(textwrap.dedent("""
            FROM node:18
            WORKDIR /app
            COPY . .
            RUN npm install
            CMD ["node", "server.js"]
        """))

def generate_docker_compose(components):
    path = f'skeleton/'
    os.makedirs(path, exist_ok=True)
    with open(os.path.join(path, 'docker-compose.yml'), 'w') as f:
        sorted_components = dict(sorted(components.items(), key=lambda item: 0 if item[1] == "database" else 1))
        f.write("services:\n")
        db = None
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
                if ctype == "backend":
                    f.write(f"    depends_on:\n      - {db}\n")
        f.write("\nnetworks:\n  default:\n    driver: bridge\n")

def apply_transformations(model):
    components = {}
    backend_name = None
    database_name = None
    for e in model.elements:
        if e.__class__.__name__ == 'Component':
            if e.type == 'backend':
                backend_name = e.name
            elif e.type == 'database':
                database_name = e.name
    for e in model.elements:
        if e.__class__.__name__ == 'Component':
            components[e.name] = e.type
            if e.type == 'database':
                generate_database(e.name)
            elif e.type == 'backend':
                generate_backend(e.name, database=database_name)
            elif e.type == 'frontend':
                generate_frontend(e.name, backend=backend_name)
            elif e.type == 'load_balancer':
                generate_load_balancer(e.name, backend=backend_name)
    generate_docker_compose(components)
```

Luego, se modifica el archivo model.arch con el fin de incluir las interacciones con el balanceador de carga, como se aprecia seguidamente: 
```ebnf
architecture:

    component frontend lssa_fe
    component backend lssa_be
    component database lssa_db
    component load_balancer lssa_lb

    connector http lssa_fe -> lssa_lb
    connector http lssa_lb -> lssa_be
    connector db_connector lssa_be -> lssa_db

```

Los archivos metamodel.py, generation.py and Dockerfile, no fue necesario modificarlos. Con los cambios, ilustrados anteriormente, se incluyo el componente del balanceador de carga al laboratorio. 
