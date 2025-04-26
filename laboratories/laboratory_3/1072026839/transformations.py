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
                // Check if token exists in session
                const token = req.query.token;
                if (!token) {{
                    return res.redirect('/login-page');
                }}

                try {{
                    const response = await axios.get(`${{API_GATEWAY_URL}}/data`, {{
                        headers: {{
                            'Authorization': token
                        }}
                    }});
                    
                    const systems = response.data.systems;
                    let list = systems.map(([id, name]) => `<li>${{name}}</li>`).join('');
                    
                    res.send(`
                    <html>
                        <body>
                            <h1>Frontend</h1>
                            <form method="POST" action="/create">
                                <input name="name" />
                                <input type="hidden" name="token" value="${{token}}" />
                                <button type="submit">Create</button>
                            </form>
                            <ul>${{list}}</ul>
                        </body>
                    </html>
                    `);
                }} catch (err) {{
                    console.error("Error:", err.message);
                    res.status(500).send("Error contacting API Gateway or unauthorized. <a href='/login-page'>Login again</a>");
                }}
            }});

            app.get('/login-page', (req, res) => {{
                res.send(`
                <html>
                    <body>
                        <h2>Please login first</h2>
                        <p>You need to login to access the system</p>
                        <p>Redirect to <a href="http://localhost:8003">login page</a></p>
                    </body>
                </html>
                `);
            }});

            app.post('/create', async (req, res) => {{
                const name = req.body.name;
                const token = req.body.token;
                
                try {{
                    await axios.post(`${{API_GATEWAY_URL}}/create`, {{ name }}, {{
                        headers: {{
                            'Authorization': token
                        }}
                    }});
                    res.redirect(`/?token=${{token}}`);
                }} catch (err) {{
                    console.error("Error:", err.message);
                    res.status(500).send("Error creating item or unauthorized. <a href='/login-page'>Login again</a>");
                }}
            }});

            app.listen(80, () => console.log("Frontend running on port 80"));
            """
        ))

def generate_login_frontend(name, api_gateway):
    path = f'skeleton/{name}'
    os.makedirs(path, exist_ok=True)

    with open(os.path.join(path, 'package.json'), 'w') as f:
        f.write(textwrap.dedent("""
            {
                "name": "login-frontend",
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

            app.get('/', (req, res) => {{
                res.send(`
                <html>
                    <body>
                        <h1>Login Page</h1>
                        <form method="POST" action="/login">
                            <div>
                                <label for="username">Username:</label>
                                <input id="username" name="username" required />
                            </div>
                            <div style="margin-top: 10px;">
                                <label for="password">Password:</label>
                                <input id="password" name="password" type="password" required />
                            </div>
                            <div style="margin-top: 10px;">
                                <button type="submit">Login</button>
                            </div>
                        </form>
                        <p style="color: gray; margin-top: 20px;">
                            Default credentials: user1 / password123
                        </p>
                    </body>
                </html>
                `);
            }});

            app.post('/login', async (req, res) => {{
                const {{ username, password }} = req.body;
                
                try {{
                    const response = await axios.post(`${{API_GATEWAY_URL}}/login`, {{ username, password }});
                    const token = response.data.token;
                    
                    // Redirect to main frontend with token
                    res.redirect(`http://localhost:8002/?token=${{token}}`);
                }} catch (err) {{
                    console.error("Login error:", err.message);
                    res.status(401).send(`
                        <html>
                            <body>
                                <h2>Invalid credentials</h2>
                                <p>Please try again</p>
                                <a href="/">Back to login</a>
                            </body>
                        </html>
                    `);
                }}
            }});

            app.listen(80, () => console.log("Login Frontend running on port 80"));
            """
        ))
        
def generate_load_balancer(name, backend_names):
    path = f'skeleton/{name}'
    os.makedirs(path, exist_ok=True)

    upstream_servers = '\n'.join([f'        server {backend}:80;' for backend in backend_names])

    with open(os.path.join(path, 'nginx.conf'), 'w') as f:
        f.write(textwrap.dedent(f"""
            user nginx;
            worker_processes 1;
            
            error_log /var/log/nginx/error.log warn;
            pid /var/run/nginx.pid;
                                
            events {{
                worker_connections 1024;
            }}
                                
            http {{
                include /etc/nginx/mime.types;
                default_type application/octet-stream;
                                
                log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                              '$status $body_bytes_sent "$http_referer" '
                              '"$http_user_agent" "$http_x_forwarded_for"';
                                
                access_log /var/log/nginx/access.log main;
                                
                sendfile on;
                keepalive_timeout 65;
                                
                upstream backend_servers {{
                    {upstream_servers}
                }}

                server {{
                    listen 80;
                    
                    location / {{
                        proxy_pass http://backend_servers;
                        proxy_set_header Host $host;
                        proxy_set_header X-Real-IP $remote_addr;
                        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                        proxy_set_header X-Forwarded-Proto $scheme;
                    }}
                }}
            }}
            """
        ))

    with open(os.path.join(path, 'Dockerfile'), 'w') as f:
        f.write(textwrap.dedent("""
            FROM nginx:1.21-alpine
            
            COPY nginx.conf /etc/nginx/nginx.conf
            
            EXPOSE 80
            
            CMD ["nginx", "-g", "daemon off;"]
            """
        ))

def generate_api_gateway(name, load_balancer):
    path = f'skeleton/{name}'
    os.makedirs(path, exist_ok=True)

    with open(os.path.join(path, 'app.py'), 'w') as f:
        f.write(textwrap.dedent(f"""
            from flask import Flask, request, jsonify
            import jwt
            from functools import wraps
            import requests

            app = Flask(__name__)
            SECRET_KEY = "your_secret_key"
            AUTHORIZED_IP = "127.0.0.1"  # Solo permitir acceso local por simplicidad
            LOAD_BALANCER_URL = "http://{load_balancer}:80"

            # Usuarios de ejemplo para este ejercicio
            USERS = {{
                "user1": "password123"
            }}

            # Función para verificar si la solicitud proviene de una dirección IP autorizada
            def limit_exposure(f):
                @wraps(f)
                def decorated_function(*args, **kwargs):
                    client_ip = request.remote_addr
                    if client_ip != AUTHORIZED_IP:
                        return jsonify({{'message': 'Forbidden: Unauthorized IP'}}), 403
                    return f(*args, **kwargs)
                return decorated_function

            # Función para verificar el token JWT
            def token_required(f):
                @wraps(f)
                def decorated_function(*args, **kwargs):
                    token = request.headers.get('Authorization')
                    if not token:
                        return jsonify({{'message': 'Token is missing!'}}), 403
                    try:
                        jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
                    except:
                        return jsonify({{'message': 'Token is invalid!'}}), 403
                    return f(*args, **kwargs)
                return decorated_function

            # Ruta para el inicio de sesión del usuario (devuelve token JWT)
            @app.route('/login', methods=['POST'])
            def login():
                auth = request.get_json()
                username = auth.get('username')
                password = auth.get('password')
                
                if USERS.get(username) == password:
                    token = jwt.encode({{'username': username}}, SECRET_KEY, algorithm="HS256")
                    return jsonify({{'token': token}})
                return jsonify({{'message': 'Invalid credentials'}}), 401

            # Ruta protegida para crear un nuevo sistema
            @app.route('/create', methods=['POST'])
            @token_required
            @limit_exposure
            def create_system():
                try:
                    response = requests.post(f'{{LOAD_BALANCER_URL}}/create', json=request.get_json())
                    return jsonify(response.json()), response.status_code
                except Exception as e:
                    return jsonify({{'message': f'Error accessing load balancer: {{str(e)}}'}}), 500

            # Ruta protegida para obtener todos los sistemas
            @app.route('/data', methods=['GET'])
            @token_required
            @limit_exposure
            def get_data():
                try:
                    response = requests.get(f'{{LOAD_BALANCER_URL}}/systems')
                    return jsonify(response.json()), response.status_code
                except Exception as e:
                    return jsonify({{'message': f'Error accessing load balancer: {{str(e)}}'}}), 500

            if __name__ == "__main__":
                app.run(host='0.0.0.0', port=80)
            """
        ))

    with open(os.path.join(path, 'Dockerfile'), 'w') as f:
        f.write(textwrap.dedent("""
            FROM python:3.11-slim
            
            WORKDIR /app
            COPY . .
            RUN pip install flask pyjwt requests
            
            CMD ["python", "app.py"]
            """
        ))

def generate_docker_compose(components, backend_names):
    path = f'skeleton/'
    os.makedirs(path, exist_ok=True)

    with open(os.path.join(path, 'docker-compose.yml'), 'w') as f:
        # Ordenar componentes para que la base de datos y api_gateway sean los primeros
        sorted_components = dict(sorted(components.items(), key=lambda item: 0 if item[1] == "database" else (1 if item[1] == "api_gateway" else 2)))

        f.write("services:\n")

        # Almacenar referencia a los nombres de los componentes especiales
        database_name = None
        api_gateway_name = None
        load_balancer_name = None

        for i, (name, ctype) in enumerate(sorted_components.items()):
            if ctype == "database":
                database_name = name
            elif ctype == "api_gateway":
                api_gateway_name = name
            elif ctype == "load_balancer":
                load_balancer_name = name

        # Generar la configuración para cada componente
        for i, (name, ctype) in enumerate(sorted_components.items()):
            port = 8000 + i
            f.write(f"  {name}:\n")
            if ctype == "database":
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
                
                # Configurar dependencias
                if ctype == "backend":
                    f.write(f"    depends_on:\n      - {database_name}\n")
                elif ctype == "load_balancer":
                    f.write("    depends_on:\n")
                    for backend in backend_names:
                        f.write(f"      - {backend}\n")
                elif ctype == "api_gateway":
                    f.write(f"    depends_on:\n      - {load_balancer_name}\n")
                elif ctype == "frontend":
                    f.write(f"    depends_on:\n      - {api_gateway_name}\n")

        f.write("\nnetworks:\n  default:\n    driver: bridge\n")

def apply_transformations(model):
    components = {}
    backend_names = []
    database_name = None
    load_balancer_name = None
    api_gateway_name = None
    main_frontend_name = None
    login_frontend_name = None

    # Primera pasada para identificar todos los componentes
    for e in model.elements:
        if e.__class__.__name__ == 'Component':
            components[e.name] = e.type
            if e.type == 'backend':
                backend_names.append(e.name)
            elif e.type == 'database':
                database_name = e.name
            elif e.type == 'load_balancer':
                load_balancer_name = e.name
            elif e.type == 'api_gateway':
                api_gateway_name = e.name
    
    # Identificar los frontends
    frontends = [name for name, ctype in components.items() if ctype == 'frontend']
    if len(frontends) >= 2:
        login_frontend_name = frontends[0]  # Asumimos que el primer frontend es para login
        main_frontend_name = frontends[1]   # Y el segundo es el frontend principal
    
    # Segunda pasada para generar los componentes
    for e in model.elements:
        if e.__class__.__name__ == 'Component':
            if e.type == 'database':
                generate_database(e.name)
            elif e.type == 'backend':
                generate_backend(e.name, database=database_name)
            elif e.type == 'load_balancer':
                generate_load_balancer(e.name, backend_names=backend_names)
            elif e.type == 'api_gateway':
                generate_api_gateway(e.name, load_balancer=load_balancer_name)
            elif e.type == 'frontend':
                if e.name == main_frontend_name:
                    generate_frontend(e.name, api_gateway=api_gateway_name)
                elif e.name == login_frontend_name:
                    generate_login_frontend(e.name, api_gateway=api_gateway_name)
    
    generate_docker_compose(components, backend_names)