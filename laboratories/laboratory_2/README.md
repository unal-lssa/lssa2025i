 Large-Scale Software Architecture
# Laboratory 2 - Modeling

## 1. Objective

The objective of this lab is to apply the Model-Driven Software Engineering (MDE) paradigm in order to automate the generation of the skeleton of a software system from an architectural perspective. Students will create a computer program to define a DSL-based metamodel, define a set of transformation rules, define a model (as a metamodel instance) and execute the generation process.

*DSL: Domain-Specific Language.*

## 2. Prerequisites

A computer with [Docker](https://docs.docker.com/engine/install/) installed.

## 3. Instructions

### 3.1. Metamodeling

**a.** Create an **arch.tx** file in order to define the grammar of a Domain-Specific Language (DSL):

```tx
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
    'frontend' | 'backend' | 'database'
;

ConnectorType:
    'http' | 'db_connector'
;
```

**b.** Create a **metamodel.py** file in order to create the metamodel from the DSL grammar:

```python
import os

from textx import metamodel_from_file

def create_metamodel():
    grammar = os.path.join(os.path.dirname(__file__), 'arch.tx')
    return metamodel_from_file(grammar)
```

### 3.2. Transformations

Create a **transformations.py** file in order to automatically generate the skeleton of the system to be modeled:

* A MySQL **database** component.
* A Python **backend** component.
* A JavaScript **frontend** component.

```python
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
                if ctype== "backend":
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
            if e.type == 'backend':
                generate_backend(e.name, database=database_name)
            elif e.type == 'frontend':
                generate_frontend(e.name, backend=backend_name)

    generate_docker_compose(components)
```

### 3.3. Modeling

Create a **model.arch** file in order to model the skeleton of the system to be modeled.

```arch
architecture:

    component frontend lssa_fe
    component backend lssa_be
    component database lssa_db

    connector http lssa_fe -> lssa_be
    connector db_connector lssa_be -> lssa_db
```

### 3.4. Generation

Create a **generation.py** file in order to generate the skeleton of the system to be modeled.
˚
```python
from metamodel import create_metamodel
from transformations import apply_transformations

if __name__ == '__main__':
    
    metamodel = create_metamodel()
    model = metamodel.model_from_file('model.arch')
    apply_transformations(model)
```

### 3.5. Testing

**a.** Create a **Dockerfile** file to specify the requirements to execute the program.

```Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir textX mysql-connector-python flask

CMD ["python", "generation.py"]
```

**b.** Create a *Docker image* from the *Dockerfile* file.

```bash
docker build -t lssa-lab2 .
```

**c.** Create a *Docker container* to execute the program and generate the modeled software system.

```bash
docker run --rm -v "$PWD:/app" lssa-lab2
```

After running the above command, a directory called skeleton should be created.

**d.** Enter to the */skeleton* directory.

**e.** Execute the generated skeleton of the modeled software system.

```bash
docker-compose up --build
```

**f.** Verify the executed containers (*skeleton-lssa_db-1*, *skeleton-lssa_be-1* and *skeleton-lssa_fe-1*):

```bash
docker ps -a
```

**g.** Open the frontend component in a web browser: `http://localhost:8001`.

**h.** Create a new element (system) using the user interface.

**i.** Check the new element in the database component:

```bash
docker exec -it skeleton-lssa_db-1 sh
```

```bash
mysql -u root -p
```

Password = *root*

```mysql
SHOW DATABASES;
```

```mysql
USE lssa_db;
```

```mysql
SELECT * FROM systems;
```

## 4. Delivery

### 4.1. Deliverable

* Full name.
* The same program with the following improvement: support of a new component type (**load balancer**). **Modify** the *arch.tx*, *transformations.py*, and *model.arch* files; and **keep** the same *metamodel.py*, *generation.py* and *Dockerfile* files.

### 4.2. Submission Format

* The deliverable must be submitted via GitHub ([lssa2025i](https://github.com/unal-lssa/lssa2025i) repository).
* Steps:
  - Use the branch corresponding to your team (team1, team2, ...).
  - In the folder [laboratories/laboratory_2](), create an **X** folder (where X = your identity document number), which must include the **deliverable**:
    + README.md with the full name.
    + *arch.tx*, *metamodel.py*, *transformations.py*, *model.arch*, *generation.py* and *Dockerfile* files.

### 4.3. Delivery Deadline

Saturday, April 12, 2025, before 23h59.