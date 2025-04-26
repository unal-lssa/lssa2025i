import os, textwrap

def generate_database(name, db_type='mysql'):
    path = f'skeleton/{name}'
    os.makedirs(path, exist_ok=True)

    if db_type.lower() == 'mysql' or db_type.lower() == 'postgresql':
        with open(os.path.join(path, 'init.sql'), 'w') as f:
            f.write(textwrap.dedent("""
                CREATE TABLE IF NOT EXISTS systems (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255)
                );
                """
            ))
    elif db_type.lower() == 'mongodb':
        with open(os.path.join(path, 'init-mongo.js'), 'w') as f:
            f.write(textwrap.dedent("""
                db = db.getSiblingDB('admin');
                db.auth('root', 'root');
                db = db.getSiblingDB('app_db');
                
                db.createCollection('systems');
                db.systems.insertOne({ name: 'example_system' });
                """
            ))
    elif db_type.lower() == 'elasticsearch':
        with open(os.path.join(path, 'init-es.sh'), 'w') as f:
            f.write(textwrap.dedent("""
                #!/bin/bash
                sleep 20 # Wait for Elasticsearch to start
                curl -X PUT "localhost:9200/systems?pretty" -H 'Content-Type: application/json' -d '
                {
                  "mappings": {
                    "properties": {
                      "name": { "type": "text" }
                    }
                  }
                }
                '
                """
            ))
            # Make the script executable
            os.chmod(os.path.join(path, 'init-es.sh'), 0o755)

def generate_backend(name, database=None, database_type='mysql', connections=None):
    path = f'skeleton/{name}'
    os.makedirs(path, exist_ok=True)
    
    # Default simple app
    app_code = textwrap.dedent("""
        from flask import Flask, jsonify

        app = Flask(__name__)

        @app.route('/')
        def hello():
            return jsonify({"message": "Hello World from Backend"})

        if __name__ == '__main__':
            app.run(host='0.0.0.0', port=80)
    """)
    
    requirements = ["flask"]
    
    # Only add connection code if this is a "from" component in a connector
    if connections:
        for conn_type, target in connections.items():
            if conn_type == "db_connector" and target:
                if database_type.lower() == 'mysql':
                    requirements.append("mysql-connector-python")
                    app_code = textwrap.dedent(f"""
                        from flask import Flask, jsonify
                        import mysql.connector

                        app = Flask(__name__)
                        
                        def get_db_connection():
                            return mysql.connector.connect(
                                host='{target}',
                                user='root',
                                password='root',
                                database='{target}'
                            )

                        @app.route('/')
                        def hello():
                            try:
                                conn = get_db_connection()
                                cursor = conn.cursor()
                                cursor.execute("SELECT 1")
                                cursor.close()
                                conn.close()
                                return jsonify({{"message": "Hello World from Backend", "database_connection": "success", "type": "MySQL"}})
                            except Exception as e:
                                return jsonify({{"message": "Hello World from Backend", "database_connection": "failed", "error": str(e)}})

                        if __name__ == '__main__':
                            app.run(host='0.0.0.0', port=80)
                    """)
                    
                elif database_type.lower() == 'mongodb':
                    requirements.append("pymongo")
                    app_code = textwrap.dedent(f"""
                        from flask import Flask, jsonify
                        from pymongo import MongoClient

                        app = Flask(__name__)
                        
                        def get_db_connection():
                            client = MongoClient('mongodb://{target}:27017/',
                                                username='root',
                                                password='root',
                                                authSource='admin')
                            return client.app_db

                        @app.route('/')
                        def hello():
                            try:
                                db = get_db_connection()
                                # Simple test query
                                result = db.systems.find_one()
                                return jsonify({{"message": "Hello World from Backend", "database_connection": "success", "type": "MongoDB", "data": result.get('name', 'No data')}})
                            except Exception as e:
                                return jsonify({{"message": "Hello World from Backend", "database_connection": "failed", "error": str(e)}})

                        if __name__ == '__main__':
                            app.run(host='0.0.0.0', port=80)
                    """)
                elif database_type.lower() == 'postgresql':
                    requirements.append("psycopg2-binary")
                    app_code = textwrap.dedent(f"""
                        from flask import Flask, jsonify
                        import psycopg2

                        app = Flask(__name__)
                        
                        def get_db_connection():
                            return psycopg2.connect(
                                host='{target}',
                                database='{target}',
                                user='postgres',
                                password='root'
                            )

                        @app.route('/')
                        def hello():
                            try:
                                conn = get_db_connection()
                                cursor = conn.cursor()
                                cursor.execute("SELECT 1")
                                cursor.close()
                                conn.close()
                                return jsonify({{"message": "Hello World from Backend", "database_connection": "success", "type": "PostgreSQL"}})
                            except Exception as e:
                                return jsonify({{"message": "Hello World from Backend", "database_connection": "failed", "error": str(e)}})

                        if __name__ == '__main__':
                            app.run(host='0.0.0.0', port=80)
                    """)
                elif database_type.lower() == 'elasticsearch':
                    requirements.append("elasticsearch")
                    app_code = textwrap.dedent(f"""
                        from flask import Flask, jsonify
                        from elasticsearch import Elasticsearch

                        app = Flask(__name__)
                        
                        def get_db_connection():
                            return Elasticsearch(['http://{target}:9200'])

                        @app.route('/')
                        def hello():
                            try:
                                es = get_db_connection()
                                # Simple test query
                                health = es.cluster.health()
                                return jsonify({{"message": "Hello World from Backend", "database_connection": "success", "type": "Elasticsearch", "health": health['status']}})
                            except Exception as e:
                                return jsonify({{"message": "Hello World from Backend", "database_connection": "failed", "error": str(e)}})

                        if __name__ == '__main__':
                            app.run(host='0.0.0.0', port=80)
                    """)
                else:  # default case
                    requirements.append("mysql-connector-python")
                    app_code = textwrap.dedent(f"""
                        from flask import Flask, jsonify

                        app = Flask(__name__)
                        
                        @app.route('/')
                        def hello():
                            return jsonify({{"message": "Hello World from Backend", "database_connection": "not configured", "type": "Unknown"}})

                        if __name__ == '__main__':
                            app.run(host='0.0.0.0', port=80)
                    """)

    with open(os.path.join(path, 'app.py'), 'w') as f:
        f.write(app_code)

    with open(os.path.join(path, 'Dockerfile'), 'w') as f:
        requirements_str = ' '.join(requirements)
        f.write(textwrap.dedent(f"""
            FROM python:3.11-slim
                                
            WORKDIR /app
            COPY . .
            RUN pip install {requirements_str}
                                
            CMD ["python", "app.py"]
            """
        ))


def generate_frontend(name, backend=None, connections=None):
    path = f'skeleton/{name}'
    os.makedirs(path, exist_ok=True)

    # Default simple app
    app_code = textwrap.dedent("""
        const express = require('express');
        const app = express();

        app.get('/', (req, res) => {
            res.send('<h1>Hello World from Frontend</h1>');
        });

        app.listen(80, () => console.log("Frontend running on port 80"));
    """)

    # Only add connection code if this is a "from" component in a connector
    if connections:
        for conn_type, target in connections.items():
            if conn_type == "http" and target:
                app_code = textwrap.dedent(f"""
                    const express = require('express');
                    const axios = require('axios');
                    const app = express();
                    
                    const BACKEND_URL = 'http://{target}:80';

                    app.get('/', async (req, res) => {{
                        try {{
                            const response = await axios.get(BACKEND_URL);
                            res.send(`
                                <h1>Hello World from Frontend</h1>
                                <p>Backend response: ${{JSON.stringify(response.data)}}</p>
                            `);
                        }} catch (err) {{
                            res.send(`
                                <h1>Hello World from Frontend</h1>
                                <p>Error connecting to backend: ${{err.message}}</p>
                            `);
                        }}
                    }});

                    app.listen(80, () => console.log("Frontend running on port 80"));
                """)

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
        f.write(app_code)

def generate_docker_compose(components, replicas=None, load_balancer_config=None, db_types=None):
    path = f'skeleton/'
    os.makedirs(path, exist_ok=True)
    
    if replicas is None:
        replicas = {}
    
    if load_balancer_config is None:
        load_balancer_config = {}

    if db_types is None:
        db_types = {}

    with open(os.path.join(path, 'docker-compose.yml'), 'w') as f:
        sorted_components = dict(sorted(components.items(), key=lambda item: 0 if item[1] == "database" or item[1] == "db" else 1))
        f.write("services:\n")

        db = None
        port_counter = 8001
        
        for name, ctype in sorted_components.items():
            if ctype == "database" or ctype == "db":
                db = name
                db_type = db_types.get(name, 'mysql').lower()
                
                if db_type == 'mysql':
                    f.write(f"  {name}:\n")
                    f.write("    image: mysql:8\n")
                    f.write("    environment:\n")
                    f.write("      - MYSQL_ROOT_PASSWORD=root\n")
                    f.write(f"      - MYSQL_DATABASE={name}\n")
                    f.write("    volumes:\n")
                    f.write(f"      - ./{name}/init.sql:/docker-entrypoint-initdb.d/init.sql\n")
                    f.write("    ports:\n")
                    f.write("      - '3306:3306'\n")
                
                elif db_type == 'postgresql':
                    f.write(f"  {name}:\n")
                    f.write("    image: postgres:14\n")
                    f.write("    environment:\n")
                    f.write("      - POSTGRES_PASSWORD=root\n")
                    f.write(f"      - POSTGRES_DB={name}\n")
                    f.write("    volumes:\n")
                    f.write(f"      - ./{name}/init.sql:/docker-entrypoint-initdb.d/init.sql\n")
                    f.write("    ports:\n")
                    f.write("      - '5432:5432'\n")
                
                elif db_type == 'mongodb':
                    f.write(f"  {name}:\n")
                    f.write("    image: mongo:6\n")
                    f.write("    environment:\n")
                    f.write("      - MONGO_INITDB_ROOT_USERNAME=root\n")
                    f.write("      - MONGO_INITDB_ROOT_PASSWORD=root\n")
                    f.write("    volumes:\n")
                    f.write(f"      - ./{name}/init-mongo.js:/docker-entrypoint-initdb.d/init-mongo.js:ro\n")
                    f.write("    ports:\n")
                    f.write("      - '27017:27017'\n")
                
                elif db_type == 'elasticsearch':
                    f.write(f"  {name}:\n")
                    f.write("    image: elasticsearch:7.17.0\n")
                    f.write("    environment:\n")
                    f.write("      - discovery.type=single-node\n")
                    f.write("      - bootstrap.memory_lock=true\n")
                    f.write("      - \"ES_JAVA_OPTS=-Xms512m -Xmx512m\"\n")
                    f.write("    volumes:\n")
                    f.write(f"      - ./{name}/init-es.sh:/init-es.sh:ro\n")
                    f.write("    command: [\"/bin/sh\", \"-c\", \"elasticsearch & /init-es.sh\"]\n")
                    f.write("    ports:\n")
                    f.write("      - '9200:9200'\n")
        
        for name, ctype in sorted_components.items():
            if ctype == "database" or ctype == "db":
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
                
                if (ctype == "backend") and db:
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

def process_connectors(model):
    """Process all connectors in the model and return a mapping of component connections."""
    component_connections = {}
    
    for e in model.elements:
        if e.__class__.__name__ == 'Connector':
            # Use getattr to avoid 'from' reserved keyword issue
            source_component = getattr(e, 'from').name
            to_component = e.to.name
            conn_type = e.type
            
            if source_component not in component_connections:
                component_connections[source_component] = {}
            
            component_connections[source_component][conn_type] = to_component
    
    return component_connections

def apply_transformations(model):
    components = {}
    replicas = {}
    load_balancer_config = {}
    database_name = None
    db_types = {}
    
    # Process components first
    for e in model.elements:
        if e.__class__.__name__ == 'Component' or e.__class__.__name__ == 'StandardComponent':
            components[e.name] = e.type
            
            if e.type == 'database' or e.type == 'db':
                database_name = e.name
                if hasattr(e, 'databaseType'):
                    db_types[e.name] = e.databaseType
                
            if hasattr(e, 'instances') and e.instances is not None:
                replicas[e.name] = e.instances.count
        
        elif e.__class__.__name__ == 'Database':
            components[e.name] = 'db'
            database_name = e.name
            if hasattr(e, 'databaseType'):
                db_types[e.name] = e.databaseType
        
        elif e.__class__.__name__ == 'LoadBalancer':
            load_balancer_name = e.name
            components[load_balancer_name] = 'loadbalancer'
            
            if hasattr(e, 'target') and e.target is not None:
                target_name = e.target.name
                load_balancer_config[load_balancer_name] = target_name
                
                if target_name not in replicas and hasattr(e, 'instanceCount'):
                    replicas[target_name] = e.instanceCount
    
    # Process connectors
    component_connections = process_connectors(model)
    
    # Generate components with their connections
    for e in model.elements:
        if e.__class__.__name__ == 'Component' or e.__class__.__name__ == 'StandardComponent':
            if e.type == 'database' or e.type == 'db':
                generate_database(e.name, db_types.get(e.name, 'mysql'))
            elif e.type == 'backend':
                connections = component_connections.get(e.name, {})
                
                # Determine database type based on connection
                backend_db_type = 'mysql'  # default
                if connections and 'db_connector' in connections:
                    connected_db = connections['db_connector']
                    if connected_db in db_types:
                        backend_db_type = db_types[connected_db]
                
                generate_backend(e.name, database=database_name, database_type=backend_db_type, connections=connections)
            elif e.type == 'frontend':
                # Connect frontend to load balancer if it exists, otherwise connect to backend
                backend_service = None
                target_name = None
                for lb_name, target_name in load_balancer_config.items():
                    backend_service = lb_name
                    break
                
                connections = component_connections.get(e.name, {})
                generate_frontend(e.name, backend=backend_service if backend_service else target_name,
                                 connections=connections)
        
        elif e.__class__.__name__ == 'Database':
            generate_database(e.name, e.databaseType if hasattr(e, 'databaseType') else 'mysql')
            
        elif e.__class__.__name__ == 'LoadBalancer':
            target_name = load_balancer_config.get(e.name)
            if target_name:
                replica_count = replicas.get(target_name, 1)
                generate_loadbalancer(e.name, target_name, replica_count)

    generate_docker_compose(components, replicas, load_balancer_config, db_types)
