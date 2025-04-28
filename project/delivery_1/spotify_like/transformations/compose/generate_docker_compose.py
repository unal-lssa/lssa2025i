import os

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
                    port_counter += 1
                    f.write(f"  {name}:\n")
                    f.write("    image: mysql:8\n")
                    f.write("    environment:\n")
                    f.write("      - MYSQL_ROOT_PASSWORD=root\n")
                    f.write(f"      - MYSQL_DATABASE={name}\n")
                    f.write("    volumes:\n")
                    f.write(f"      - ./{name}/init.sql:/docker-entrypoint-initdb.d/init.sql\n")
                    f.write("    ports:\n")
                    f.write(f"      - '{port_counter}:{port_counter}'\n")
                
                elif db_type == 'postgresql':
                    port_counter += 1
                    f.write(f"  {name}:\n")
                    f.write("    image: postgres:14\n")
                    f.write("    environment:\n")
                    f.write("      - POSTGRES_PASSWORD=root\n")
                    f.write(f"      - POSTGRES_DB={name}\n")
                    f.write("    volumes:\n")
                    f.write(f"      - ./{name}/init.sql:/docker-entrypoint-initdb.d/init.sql\n")
                    f.write("    ports:\n")
                    f.write(f"      - '{port_counter}:{port_counter}'\n")
                
                elif db_type == 'mongodb':
                    port_counter += 1
                    f.write(f"  {name}:\n")
                    f.write("    image: mongo:6\n")
                    f.write("    environment:\n")
                    f.write("      - MONGO_INITDB_ROOT_USERNAME=root\n")
                    f.write("      - MONGO_INITDB_ROOT_PASSWORD=root\n")
                    f.write("    volumes:\n")
                    f.write(f"      - ./{name}/init-mongo.js:/docker-entrypoint-initdb.d/init-mongo.js:ro\n")
                    f.write("    ports:\n")
                    f.write(f"      - '{port_counter}:{port_counter}'\n")
                
                elif db_type == 'elasticsearch':
                    port_counter += 1
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
                    f.write(f"      - '{port_counter}:{port_counter}'\n")
        
        for name, ctype in sorted_components.items():
            if ctype == "database" or ctype == "db" or ctype == "bucket" or ctype == "cdn":
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
                        port_counter += 1
                        f.write("    ports:\n")
                        f.write(f"      - '{port_counter}:{port_counter}'\n")
                        
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
                        
                port_counter += 1
                f.write("    ports:\n")
                f.write(f"      - '{port_counter}:{port_counter}'\n")
                
                
            if ctype == "loadbalancer":
                target_name = load_balancer_config.get(name)
                if target_name:
                    target_replicas = replicas.get(target_name, 1)
                    f.write("    depends_on:\n")
                    for i in range(target_replicas):
                        f.write(f"      - {target_name}_{i}\n")

        buckets = {name: ctype for name, ctype in components.items() if ctype == "bucket"}
        cdns = {name: ctype for name, ctype in components.items() if ctype == "cdn"}
        has_cdn = False

        for name in buckets:
            f.write(f"  {name}:\n")
            f.write(f"    container_name: ${{LOCALSTACK_DOCKER_NAME:-{name}}}\n")
            f.write(f"    build:\n")
            f.write(f"      context: ./{name}\n")
            f.write(f"    ports:\n")
            f.write(f"      - '4566:4566'\n")
            f.write(f"    environment:\n")
            f.write(f"      - DEBUG=${{DEBUG:-0}}\n")
            f.write(f"    volumes:\n")
            f.write(f"      - ${{LOCALSTACK_VOLUME_DIR:-./volume}}:/var/lib/localstack\n")
            f.write(f"      - /var/run/docker.sock:/var/run/docker.sock\n")

        for name in cdns:
            has_cdn = True
            f.write(f"  {name}:\n")
            f.write(f"    container_name: {name}\n")
            f.write(f"    build:\n")
            f.write(f"      context: ./{name}\n")
            f.write(f"    ports:\n")
            f.write(f"      - '8080:80'\n")
            f.write(f"    volumes:\n")
            f.write(f"      - ./songs_cdn/nginx.conf:/etc/nginx/nginx.conf:ro\n")
            f.write(f"      - nginx_cache:/tmp/nginx_cache\n")

        # this MUST be at the end of the file, fokin orozco
        if has_cdn:
            f.write("\nvolumes:\n")
            f.write("  nginx_cache:\n")

        