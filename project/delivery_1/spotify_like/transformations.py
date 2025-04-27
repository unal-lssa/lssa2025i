import os, textwrap
import shutil

def generate_docker_compose(components):
    path = f'skeleton/'
    os.makedirs(path, exist_ok=True)
    
    with open(os.path.join(path, 'docker-compose.yml'), 'w') as f:
        sorted_components = dict(sorted(components.items(), key=lambda item: 0 if item[1] == "database" else 1))
        f.write("services:\n")
        
        for name, ctype in sorted_components.items():
            if ctype == "database":
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

            if ctype == "bucket":
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

def generate_bucket(name):
    path = f'skeleton/{name}'
    os.makedirs(path, exist_ok=True)

    with open(os.path.join(path, 'init-bucket.sh'), 'w') as f:
        f.write("#!/bin/bash\n")
        f.write("set -e\n")
        f.write("\n")
        f.write("awslocal s3 mb s3://music-storage\n")
        f.write("awslocal s3 cp /songs/song.mp3 s3://music-storage/song.mp3")
    
    with open(os.path.join(path, 'Dockerfile'), 'w') as f:
        f.write("FROM localstack/localstack:s3-latest\n")
        f.write("RUN apt-get update && \\\n")
        f.write("    apt-get install -y python3-pip curl && \\\n")
        f.write("    pip3 install awscli awscli-local\n")
        f.write("\n")
        f.write("COPY init-bucket.sh /etc/localstack/init/ready.d/init-bucket.sh\n")
        f.write("COPY ./song.mp3 /songs/\n")
        f.write("RUN chmod +x /etc/localstack/init/ready.d/init-bucket.sh\n")

def move_file(src, dest):
    shutil.move(src, os.path.join(dest, os.path.basename(src)))
    print(f'Archivo {src} movido a {os.path.join(dest, os.path.basename(src))}')



                    
def apply_transformations(model):
    components = {}
    replicas = {}
    load_balancer_config = {}
    database_name = None

    for e in model.elements:
        if e.__class__.__name__ == 'Component' or e.__class__.__name__ == 'StandardComponent':
            components[e.name] = e.type
            
            if e.type == 'database':
                database_name = e.name
                

    for e in model.elements:
        if e.__class__.__name__ == 'Component' or e.__class__.__name__ == 'StandardComponent':
            if e.type == 'database':
                generate_database(e.name)
            elif e.type == 'backend':
                generate_backend(e.name, database=database_name)
            elif e.type == 'frontend':
                # Connect frontend to load balancer if it exists, otherwise connect to backend
                backend_service = None
                target_name = None
                for lb_name, target_name in load_balancer_config.items():
                    backend_service = lb_name
                    break
                generate_frontend(e.name, backend=backend_service if backend_service else target_name)
            elif e.type == 'bucket':
                generate_bucket(e.name)

        elif e.__class__.__name__ == 'LoadBalancer':
            target_name = load_balancer_config.get(e.name)
            if target_name:
                replica_count = replicas.get(target_name, 1)
                generate_loadbalancer(e.name, target_name, replica_count)
            

    generate_docker_compose(components)
    src = os.path.join(os.getcwd(), 'song.mp3')
    dest = os.path.join(os.getcwd(), 'skeleton/music_storage')
    move_file(src, dest)
