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

def generate_load_balancer(name, backends):
    path = f'skeleton/{name}'
    os.makedirs(path, exist_ok=True)

    with open(os.path.join(path, 'nginx.conf'), 'w') as f:
        f.write(textwrap.dedent("""
            events {
                worker_connections 1024;
            }
            
            http {
                upstream backend_servers {
                    least_conn;
        """))
        
        # Add backends to upstream
        for backend in backends:
            f.write(f"        server {backend}:80;\n")
        
        f.write(textwrap.dedent("""
                }

                server {
                    listen 80;
                    
                    location / {
                        proxy_pass http://backend_servers;
                        proxy_set_header Host $host;
                        proxy_set_header X-Real-IP $remote_addr;
                    }
                }
            }
        """))

    with open(os.path.join(path, 'Dockerfile'), 'w') as f:
        f.write(textwrap.dedent("""
            FROM nginx:latest
            COPY nginx.conf /etc/nginx/nginx.conf
            EXPOSE 80
        """))

def generate_monitoring(name, components):
    path = f'skeleton/{name}'
    os.makedirs(path, exist_ok=True)

    # Prometheus configuration
    with open(os.path.join(path, 'prometheus.yml'), 'w') as f:
        f.write(textwrap.dedent("""
            global:
              scrape_interval: 15s
              evaluation_interval: 15s

            scrape_configs:
        """))
        
        # Add configuration for each component
        for comp_name, comp_type in components.items():
            if comp_type in ['backend', 'load_balancer']:
                f.write(textwrap.dedent(f"""
                  - job_name: '{comp_name}'
                    static_configs:
                      - targets: ['{comp_name}:80']
                        labels:
                          service: '{comp_name}'
                """))

    # Grafana dashboard setup
    os.makedirs(os.path.join(path, 'grafana/dashboards'), exist_ok=True)
    with open(os.path.join(path, 'grafana/dashboards/dashboard.json'), 'w') as f:
        f.write(textwrap.dedent("""
            {
              "annotations": {
                "list": []
              },
              "editable": true,
              "fiscalYearStartMonth": 0,
              "graphTooltip": 0,
              "links": [],
              "liveNow": false,
              "panels": [
                {
                  "datasource": {
                    "type": "prometheus",
                    "uid": "prometheus"
                  },
                  "fieldConfig": {
                    "defaults": {
                      "color": {
                        "mode": "palette-classic"
                      },
                      "custom": {
                        "axisCenteredZero": false,
                        "axisColorMode": "text",
                        "axisLabel": "",
                        "axisPlacement": "auto",
                        "barAlignment": 0,
                        "drawStyle": "line",
                        "fillOpacity": 0,
                        "gradientMode": "none",
                        "hideFrom": {
                          "legend": false,
                          "tooltip": false,
                          "viz": false
                        },
                        "lineInterpolation": "linear",
                        "lineWidth": 1,
                        "pointSize": 5,
                        "scaleDistribution": {
                          "type": "linear"
                        },
                        "showPoints": "auto",
                        "spanNulls": false,
                        "stacking": {
                          "group": "A",
                          "mode": "none"
                        },
                        "thresholdsStyle": {
                          "mode": "off"
                        }
                      },
                      "mappings": [],
                      "thresholds": {
                        "mode": "absolute",
                        "steps": [
                          {
                            "color": "green",
                            "value": null
                          }
                        ]
                      }
                    },
                    "overrides": []
                  },
                  "gridPos": {
                    "h": 8,
                    "w": 12,
                    "x": 0,
                    "y": 0
                  },
                  "id": 1,
                  "options": {
                    "legend": {
                      "calcs": [],
                      "displayMode": "list",
                      "placement": "bottom",
                      "showLegend": true
                    },
                    "tooltip": {
                      "mode": "single",
                      "sort": "none"
                    }
                  },
                  "title": "Request Rate por Servicio",
                  "type": "timeseries"
                }
              ],
              "refresh": "",
              "schemaVersion": 38,
              "style": "dark",
              "tags": [],
              "templating": {
                "list": []
              },
              "time": {
                "from": "now-6h",
                "to": "now"
              },
              "timepicker": {},
              "timezone": "",
              "title": "Sistema Monitoring",
              "version": 0,
              "weekStart": ""
            }
        """))

    # Dockerfile for Prometheus
    with open(os.path.join(path, 'Dockerfile.prometheus'), 'w') as f:
        f.write(textwrap.dedent("""
            FROM prom/prometheus
            COPY prometheus.yml /etc/prometheus/prometheus.yml
        """))

    # Dockerfile for Grafana
    with open(os.path.join(path, 'Dockerfile.grafana'), 'w') as f:
        f.write(textwrap.dedent("""
            FROM grafana/grafana
            COPY grafana/dashboards /var/lib/grafana/dashboards
        """))

def apply_transformations(model):
    components = {}
    backend_names = []
    database_name = None
    load_balancer_name = None
    monitoring_name = None

    for e in model.elements:
        if e.__class__.__name__ == 'Component':
            components[e.name] = e.type
            if e.type == 'backend':
                backend_names.append(e.name)
            elif e.type == 'database':
                database_name = e.name
            elif e.type == 'load_balancer':
                load_balancer_name = e.name
            elif e.type == 'monitoring':
                monitoring_name = e.name

    for e in model.elements:
        if e.__class__.__name__ == 'Component':
            if e.type == 'database':
                generate_database(e.name)
            elif e.type == 'backend':
                generate_backend(e.name, database=database_name)
            elif e.type == 'frontend':
                generate_frontend(e.name, backend=load_balancer_name if load_balancer_name else backend_names[0])
            elif e.type == 'load_balancer':
                generate_load_balancer(e.name, backend_names)
            elif e.type == 'monitoring':
                generate_monitoring(e.name, components)

    generate_docker_compose(components)

def generate_docker_compose(components):
    path = f'skeleton/'
    os.makedirs(path, exist_ok=True)

    with open(os.path.join(path, 'docker-compose.yml'), 'w') as f:
        sorted_components = dict(sorted(components.items(), key=lambda item: 0 if item[1] == "database" else 1))

        f.write("services:\n")

        db = None
        load_balancer = None
        monitoring = None

        for i, (name, ctype) in enumerate(sorted_components.items()):
            port = 8000 + i
            if ctype == "monitoring":
                monitoring = name
                # Configuración de Prometheus
                f.write(f"  {name}_prometheus:\n")
                f.write(f"    build:\n")
                f.write(f"      context: ./{name}\n")
                f.write(f"      dockerfile: Dockerfile.prometheus\n")
                f.write("    ports:\n")
                f.write("      - '9090:9090'\n")
                f.write("\n")
                # Configuración de Grafana
                f.write(f"  {name}_grafana:\n")
                f.write(f"    build:\n")
                f.write(f"      context: ./{name}\n")
                f.write(f"      dockerfile: Dockerfile.grafana\n")
                f.write("    ports:\n")
                f.write("      - '3000:3000'\n")
                f.write("    environment:\n")
                f.write("      - GF_SECURITY_ADMIN_PASSWORD=admin\n")
                f.write("    depends_on:\n")
                f.write(f"      - {name}_prometheus\n")
            elif ctype == "database":
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
            elif ctype == "load_balancer":
                load_balancer = name
                f.write(f"  {name}:\n")
                f.write(f"    build: ./{name}\n")
                f.write("    ports:\n")
                f.write("      - '80:80'\n")
                f.write("    depends_on:\n")
                for backend_name, backend_type in components.items():
                    if backend_type == "backend":
                        f.write(f"      - {backend_name}\n")
            else:
                f.write(f"  {name}:\n")
                f.write(f"    build: ./{name}\n")
                f.write(f"    ports:\n      - '{port}:80'\n")
                if ctype == "backend":
                    f.write(f"    depends_on:\n      - {db}\n")
                elif ctype == "frontend" and load_balancer:
                    f.write(f"    depends_on:\n      - {load_balancer}\n")

        f.write("\nnetworks:\n  default:\n    driver: bridge\n")