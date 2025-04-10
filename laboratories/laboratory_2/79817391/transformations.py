import os, textwrap

TEMPLATES_DIR = "./templates";
TEMPLATES_DIR_SERVICES = "services/containers";
TEMPLATES_DIR_DB = "services/db";
TEMPLATES_EXT = ".templ";
OUTPUT_DIR = "skeleton";

def generate_database(name):
    """Generación de script de base de datos.
    
    Args:
        name: nombre de la ruta de la carpeta del componente
    """    
    path = f'{OUTPUT_DIR}/{name}'
    os.makedirs(path, exist_ok=True)
    
    # Leo el archivo 
    db_sql= read_template('db','db.sql' + TEMPLATES_EXT);
    # escribe el archivo
    write_file(os.path.join(path, 'init.sql'), db_sql);
    
       
def generate_backend(name, database):
    """Creación del componente del backend.
    
    Args:
        name: nombre de la ruta de la carpeta del componente
        database: nombre de la base de datos
    """        
    path = f'{OUTPUT_DIR}/{name}'
    os.makedirs(path, exist_ok=True)
    
    # Lee plantilla de backend
    template_backend_app_json = read_template('backend','app.py' + TEMPLATES_EXT).replace('{database}', database);
    # Escribe el backend en la ruta de salida
    write_file(os.path.join(path, 'app.py'), template_backend_app_json);
    
    # Lee la plantilla de dockerfile para el backend
    template_dockerfile_backend = read_template('backend','Dockerfile' + TEMPLATES_EXT);    
    # Escribe el dockerfile en la ruta de salida
    write_file(os.path.join(path, 'Dockerfile'), template_dockerfile_backend);
    
      
        
def generate_frontend(name, backend):
    """Creación del componente frontend.
    
    Args:
        name: nombre de la ruta de la carpeta del componente
        backend: nombre del componente backend
    """       

    path = f'{OUTPUT_DIR}/{name}'
    os.makedirs(path, exist_ok=True)
    
    # leo la plantilla
    template_package_json = read_template('frontend','package.json' + TEMPLATES_EXT);
    
    # escribo el archivo
    write_file(os.path.join(path, 'package.json'), template_package_json);
     
    # Leo la plantilla de dockerfile para el frontend
    template_dockerfile_frontend = read_template('frontend','Dockerfile' + TEMPLATES_EXT);
    # Escribo el dockerfile en la ruta de salida
    write_file(os.path.join(path, 'Dockerfile'), template_dockerfile_frontend);
    
    # Leo la plantilla de app.js para el frontend
    template_app_js = read_template('frontend','app.js' + TEMPLATES_EXT).replace('{backend}', backend);
    # Escribo el app.js en la ruta de salida
    write_file(os.path.join(path, 'app.js'), template_app_js);
        

 
def generate_load_balancer(name):
    """Creación del componente load-balancer.
    
    Args:
        name: nombre con la ruta del componente
    """    
    path = f'{OUTPUT_DIR}/{name}'
    os.makedirs(path, exist_ok=True) 
    
    template_nginx_config =  read_template('balancer','nginx.conf' + TEMPLATES_EXT)
    write_file(os.path.join(path, 'nginx.conf'),template_nginx_config);
    
    template_nginx_docker  = read_template('balancer','Dockerfile' + TEMPLATES_EXT)
    write_file(os.path.join(path, 'Dockerfile'), template_nginx_docker);
    
        
def generate_docker_compose(components):
    """Genera el docker compose.
    
    Args:
        components: componentes del modelo para generar los servicios
    """    
    path = f'{OUTPUT_DIR}/'
    os.makedirs(path, exist_ok=True)
    
    services = [];
   
    docker_compose_content= "";
    
    with open(os.path.join(path, 'docker-compose.yml'), 'w') as f:
        sorted_components = dict(sorted(components.items(), key=lambda  item: 0 if item[1] == "database" else 1))

        db = None
        services.append("services:\n")
        for i, (name, ctype) in enumerate(sorted_components.items()):
            port = 8000 + i
          
            match ctype:
                case 'database' :
                    content_db = read_template(TEMPLATES_DIR_DB,'service-db.yml').replace('{name}', name);
                    services.append(
                        content_db.replace('{container_name}', name)
                        .replace('{image}', 'mysql:8')
                        .replace('{port}', '3307:3307') + '\n');
                    
                                    
                case 'backend':
                    content_backend = read_template(TEMPLATES_DIR_SERVICES,'service-depends-on.yml');
                    
                    if(name == 'lssa_be' ):
                        services.append( # servicio backend lssa_be 
                            content_backend
                            .replace('{container_name}', name)
                            .replace('{build}', f'./{name}')
                            .replace('{name_instance}', f'{name}')
                            .replace('{port}', f'{port}:80')
                            .replace('{depends}', '- lssa_db') + '\n');    
                    
                    if(name == 'lssa_be1' ):
                        services.append( # servicio backend lssa_be1
                            content_backend
                            .replace('{container_name}', f'{name}')
                            .replace('{build}', f'./{name}')
                            .replace('{name_instance}', f'{name}')
                            .replace('{port}', f'{port + 1}:80')
                            .replace('{depends}', '- lssa_db') + '\n');  
                    
                case 'frontend':
                    content_frontend = read_template(TEMPLATES_DIR_SERVICES,'service-depends-off.yml');
                    services.append(
                        content_frontend
                        .replace('{container_name}', name)
                        .replace('{build}', f'./{name}')
                        .replace('{port}', f"{port}:80 \n      - 2222:22 ") + '\n');
                
                case 'load-balancer':
                    content_load_balancer = read_template(TEMPLATES_DIR_SERVICES,'service-depends-on.yml');
                    services.append(
                        content_load_balancer
                        .replace('{container_name}', name)
                        .replace('{build}', f'./{name}')
                        .replace('{name_instance}', name)
                        .replace('{port}', '9091:9091')
                        .replace('{depends}', '- lssa_be') + '\n');
                
                case _:
                    print("Tipo no reconocido")

        # Adiciono la red para todos los componentes  
        services.append("\nnetworks:\n  default:\n   driver: bridge\n")    
        print("Docker compose generado") 
        
        docker_compose_content = "\n".join(services);        
        f.write(docker_compose_content);
           
def apply_transformations(model):
    """Aplica las transformaciones al modelo.
    
    Args:
        modelo: Modelo para aplicar transformaciones        
    """
    components = {}
    backend_name = None
    balancer_name = None
    database_name = None
    for e in model.elements:
        if e.__class__.__name__ == 'Component':
            if e.type == 'backend':
                backend_name = e.name
            if e.type == 'load-balancer':
                balancer_name = e.name
            elif e.type == 'database':
                database_name = e.name            

    
    for e in model.elements:
        if e.__class__.__name__ == 'Component':
            components[e.name] = e.type
        if e.type == 'database':
            generate_database(e.name)
        if e.type == 'backend':
            generate_backend(e.name, database=database_name)
        if e.type == 'load-balancer':
            generate_load_balancer(e.name)        
        elif e.type == 'frontend':
            generate_frontend(e.name, backend=balancer_name)
        
    generate_docker_compose(components)                
    

   
def write_file(path, content):
    """Escribe un archivo.
    
    Args:
        path: ruta completa para guardar un archivo
        content : contenido para escribir en el archivo
    """    
    with open(path, 'w') as f:
        f.write(content)    
        
        
def read_template(directory, template_name):
    """Lee un archivo desde el disco
    
    Args:
        directoriy: Directorio especifico para leer el archivo
        template_name: Nombre del archivo a leer
    """
    with open(os.path.join(TEMPLATES_DIR, directory, template_name), 'r') as f:
        return f.read()        