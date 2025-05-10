# Large-Scale Software Architecture  
## Laboratory 2 - Modeling  
#### Julián Ricardo Beltrán Lizarazo - jrbeltranl@unal.edu.co - 1023949483

## Adding Support for a Load Balancer

### Modifying the *arch.tx* File

The following modifications were made:

1. Added the *LoadBalancer* element and its corresponding definition. This allows us to define a load balancer with a given name and a list of targets for load balancing.
```tx
Element:
    Component | Connector | LoadBalancer
;

LoadBalancer:
    'load_balancer' name=ID 'targets' '[' targets+=[Component] (',' targets+=[Component])* ']'
;
```

2. Created a new element *Node* that groups *LoadBalancer* and *Component* elements. This enables us to use *Node* in the connector definition, allowing connectors between *Component* and *LoadBalancer* elements.
```tx
Node:
    LoadBalancer | Component
;
```

3. Updated the *Connector* definition.
```tx
Connector:
    'connector' type=ConnectorType from=[Node] '->' to=[Node]
;
```

### Modifying the *model.arch* File

The *load_balancer* element was added, and the connector for the front end was updated to target the load balancer instead of the back end directly.

```arch
architecture:

    component frontend lssa_fe

    load_balancer lssa_lb targets [lssa_be]

    component backend lssa_be
    component database lssa_db

    connector http lssa_fe -> lssa_lb
    connector db_connector lssa_be -> lssa_db
```

### Modifying the *transformations.py* File

Added a function to generate the load balancer.
```python
def generate_load_balancer(name, backend_names):
    if not backend_names:
        print(f"⚠️ Skipping load balancer '{name}' — no targets defined.")
        return

    path = f'skeleton/{name}'
    os.makedirs(path, exist_ok=True)

    with open(os.path.join(path, 'nginx.conf'), 'w') as f:
        upstream = "\n".join([f"        server {b}:80;" for b in backend_names])
        f.write(textwrap.dedent(f"""
            events {{}}
            http {{
                upstream backend_cluster {{
                    {upstream}
                }}
                server {{
                    listen 80;
                    location / {{
                        proxy_pass http://backend_cluster;
                    }}
                }}
            }}
        """))

    with open(os.path.join(path, 'Dockerfile'), 'w') as f:
        f.write(textwrap.dedent(f"""
            FROM nginx:alpine
            COPY nginx.conf /etc/nginx/nginx.conf
        """))
```

Updated the *apply_transformations* function to first collect metadata from the elements in the model and then generate the components, including the newly added load balancer.
```python
def apply_transformations(model):
    components = {}
    backend_name = None
    database_name = None

    # Collect metadata
    for e in model.elements:
        if e.__class__.__name__ == 'Component':
            components[e.name] = e.type
            if e.type == 'backend' and not backend_name:
                backend_name = e.name
            elif e.type == 'database' and not database_name:
                database_name = e.name
        elif e.__class__.__name__ == 'LoadBalancer':
            components[e.name] = 'load_balancer'
            load_balancer_name = e.name

    # Generate components
    for e in model.elements:
        if e.__class__.__name__ == 'Component':
            if e.type == 'database':
                generate_database(e.name)
            elif e.type == 'backend':
                generate_backend(e.name, database=database_name)
            elif e.type == 'frontend':
                # Use the load balancer as the backend
                generate_frontend(e.name, backend=load_balancer_name)
        elif e.__class__.__name__ == 'LoadBalancer':
            backends = [k for k, v in components.items() if v == 'backend']
            generate_load_balancer(e.name, backend_names=backends)

    generate_docker_compose(components)
```

Updated the *generate_docker_compose* function to include the load balancer in the Docker Compose file.
```python
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
            
            # New logic to include the load balancer in the Docker Compose file
            elif ctype == "load_balancer":
                f.write(f"    build: ./{name}\n")
                f.write(f"    ports:\n      - '{port}:80'\n")
                f.write("    depends_on:\n")
                for bname, btype in components.items():
                    if btype == "backend":
                        f.write(f"      - {bname}\n")
            else:
                f.write(f"    build: ./{name}\n")
                f.write(f"    ports:\n      - '{port}:80'\n")
                if ctype == "backend":
                    f.write(f"    depends_on:\n      - {db}\n")

        f.write("\nnetworks:\n  default:\n    driver: bridge\n")
```

### Known Limitations & Future Work

Right now, the model doesn't actually use the connectors defined in the *model.arch* file when applying the transformations. Instead, it currently only supports an architecture with one front end, one back end, one database, and one load balancer element each—relying on the element type to infer the parameters needed for the generator functions.

In a future version, the code could be refactored to actually use the connectors to infer dependencies between the components and configure them with the correct addresses. This would allow for architectures with multiple elements of each type.
