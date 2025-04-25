import os
import logging

# Configurar el nivel de logging
logging.basicConfig(level=logging.DEBUG)

def generate_frontend(element):
    """
    Genera el frontend para la aplicación usando las plantillas.
    :param element: El elemento del modelo que representa el frontend.
    :return: None
    """
    # Obtener el nombre del frontend
    name = element.name
    
    # Obtener la ruta del directorio de plantillas
    templates_dir = get_templates_path(name)
    
    # Obtener la ruta del directorio de salida
    skeleton_dir = get_skeleton_path(name)

    # Crear el directorio de salida si no existe
    if not os.path.exists(skeleton_dir):
        os.makedirs(skeleton_dir)
    
    # Existen 4 archivos de plantilla para el frontend
    # 1. app.js
    # 2. Dockerfile
    # 3. package.json
    # 4. intex.html

    # Generar los archivos de plantilla
    # 1. app.js
    template_path = os.path.join(templates_dir, "app.js")
    
    with open(template_path, "r") as template_file:
        template = template_file.read()
    # Reemplazar los marcadores de posición en la plantilla
    # template = template.replace("{{MARCADOR}}", VALOR)
    # Guardar el archivo generado
    with open(os.path.join(skeleton_dir, "app.js"), "w") as output_file:
        output_file.write(template)

    # 2. Dockerfile
    template_path = os.path.join(templates_dir, "Dockerfile")
    with open(template_path, "r") as template_file:
        template = template_file.read()
    # Reemplazar los marcadores de posición en la plantilla
    # template = template.replace("{{MARCADOR}}", VALOR)
    # Guardar el archivo generado
    with open(os.path.join(skeleton_dir, "Dockerfile"), "w") as output_file:
        output_file.write(template)
    
    # 3. package.json
    template_path = os.path.join(templates_dir, "package.json")
    with open(template_path, "r") as template_file:
        template = template_file.read()
    # Reemplazar los marcadores de posición en la plantilla
    # template = template.replace("{{MARCADOR}}", VALOR)
    # Guardar el archivo generado
    with open(os.path.join(skeleton_dir, "package.json"), "w") as output_file:
        output_file.write(template)
    
    # 4. index.html
    template_path = os.path.join(templates_dir, "index.html")
    with open(template_path, "r") as template_file:
        template = template_file.read()
    # Reemplazar los marcadores de posición en la plantilla
    # template = template.replace("{{MARCADOR}}", VALOR)
    # Guardar el archivo generado
    with open(os.path.join(skeleton_dir, "index.html"), "w") as output_file:
        output_file.write(template)

def generate_api_gateway(element):
    """
    Genera el API Gateway para la aplicación usando las plantillas.
    :param element: El elemento del modelo que representa el API Gateway.
    :return: None
    """
    # Obtener el nombre del frontend
    name = element.name
            # Obtener la ruta del directorio de salida
    skeleton_dir = get_skeleton_path(name)
    
    logging.debug(f"Iniciar generando el microservicio {name}");   
        
   
    path = get_templates_path(name)   
    
    # leo la plantilla
    template_api_gateway = read_template(path,'api_gateway.py');   
    # escribo el archivo
    write_artefact(skeleton_dir, 'api_gateway.py', template_api_gateway);
     
     
    # Leo la plantilla de dockerfile para el frontend
    template_dockerfile_frontend = read_template(path,'Dockerfile');
    # Escribo el dockerfile en la ruta de salida
    write_artefact(skeleton_dir, 'Dockerfile', template_dockerfile_frontend);  
    
    # Leo la plantilla de dockerfile para el frontend
    template_requisitos = read_template(path,'requirements.txt');
    # Escribo el dockerfile en la ruta de salida
    write_artefact(skeleton_dir, 'requirements.txt', template_requisitos);  
    
    
    path = get_templates_path('shared') 
    skeleton_dir = get_skeleton_path('shared')
     # Leo la plantilla de dockerfile para el frontend
    template_shared = read_template(path,'auth_utils.py');
    # Escribo el dockerfile en la ruta de salida
    write_artefact(skeleton_dir, 'auth_utils.py', template_shared);  

def generate_load_balancer(element, targets):
    """
    Genera el Load Balancer para la aplicación usando las plantillas.
    :param element: El elemento del modelo que representa el Load Balancer.
    :return: None
    """
    # Obtener el nombre del Load Balancer
    name = element.name

    # Obtener la ruta del directorio de plantillas
    templates_dir = get_templates_path(name)

    # Obtener la ruta del directorio de salida
    skeleton_dir = get_skeleton_path(name)

    # Crear el directorio de salida si no existe
    if not os.path.exists(skeleton_dir):
        os.makedirs(skeleton_dir)
    
    # Existen 2 archivos de plantilla para el Load Balancer
    # 1. nginx.conf
    # 2. Dockerfile

    # Generar los archivos de plantilla
    # 1. nginx.conf
    template_path = os.path.join(templates_dir, "nginx.conf")
    with open(template_path, "r") as template_file:
        template = template_file.read()
    # Reemplazar los marcadores de posición en la plantilla
    # Esta versión sólo funciona si el puerto de todos los backend es 5000
    VALOR = ";".join(target + ":5000" for target in targets) + ";"
    template = template.replace("###Targets###", VALOR)
    # Guardar el archivo generado
    with open(os.path.join(skeleton_dir, "nginx.conf"), "w") as output_file:
        output_file.write(template)

    # 2. Dockerfile
    template_path = os.path.join(templates_dir, "Dockerfile")
    with open(template_path, "r") as template_file:
        template = template_file.read()
    # Reemplazar los marcadores de posición en la plantilla
    # template = template.replace("{{MARCADOR}}", VALOR)
    # Guardar el archivo generado
    with open(os.path.join(skeleton_dir, "Dockerfile"), "w") as output_file:
        output_file.write(template)

def generate_backend(element):
    """
    Genera el Backend para la aplicación usando las plantillas.
    :param element: El elemento del modelo que representa el Backend.
    :return: None
    """
    # Obtener el nombre del Backend
    name = element.name

    # Obtener la ruta del directorio de plantillas
    templates_dir = get_templates_path(name)

    # Obtener la ruta del directorio de salida
    skeleton_dir = get_skeleton_path(name)

    # Crear el directorio de salida si no existe
    if not os.path.exists(skeleton_dir):
        os.makedirs(skeleton_dir)
    
    # Existen 2 archivos de plantilla para el Backend
    # 1. app.py
    # 2. Dockerfile
    # 3. requirements.txt

    # Generar los archivos de plantilla
    # 1. app.py
    template_path = os.path.join(templates_dir, "app.py")
    with open(template_path, "r") as template_file:
        template = template_file.read()
    # Reemplazar los marcadores de posición en la plantilla
    # template = template.replace("{{MARCADOR}}", VALOR)
    # Guardar el archivo generado
    with open(os.path.join(skeleton_dir, "app.py"), "w") as output_file:
        output_file.write(template)

    # 2. Dockerfile
    template_path = os.path.join(templates_dir, "Dockerfile")
    with open(template_path, "r") as template_file:
        template = template_file.read()
    # Reemplazar los marcadores de posición en la plantilla
    # template = template.replace("{{MARCADOR}}", VALOR)
    # Guardar el archivo generado
    with open(os.path.join(skeleton_dir, "Dockerfile"), "w") as output_file:
        output_file.write(template)
    
    # 3. requirements.txt
    template_path = os.path.join(templates_dir, "requirements.txt")
    with open(template_path, "r") as template_file:
        template = template_file.read()
    # Reemplazar los marcadores de posición en la plantilla
    # template = template.replace("{{MARCADOR}}", VALOR)
    # Guardar el archivo generado
    with open(os.path.join(skeleton_dir, "requirements.txt"), "w") as output_file:
        output_file.write(template)

def generate_database(element):
    """
    Genera la Base de Datos para la aplicación usando las plantillas.
    :param element: El elemento del modelo que representa la Base de Datos.
    :return: None
    """
    # Obtener el nombre de la Base de Datos
    name = element.name

    # Obtener la ruta del directorio de plantillas
    templates_dir = get_templates_path(name)

    # Obtener la ruta del directorio de salida
    skeleton_dir = get_skeleton_path(name)

    # Crear el directorio de salida si no existe
    if not os.path.exists(skeleton_dir):
        os.makedirs(skeleton_dir)
    
    # Existen 1 archivo de plantilla para la Base de Datos
    # 1. init.sql

    # Generar los archivos de plantilla
    # 1. init.sql
    template_path = os.path.join(templates_dir, "init.sql")
    with open(template_path, "r") as template_file:
        template = template_file.read()
    # Reemplazar los marcadores de posición en la plantilla
    # template = template.replace("{{MARCADOR}}", VALOR)
    # Guardar el archivo generado
    with open(os.path.join(skeleton_dir, "init.sql"), "w") as output_file:
        output_file.write(template)



def generate_docker_compose():
    """Genera el docker compose.
    
    Args:
        components: componentes del modelo para generar los servicios
    """ 
    # Obtener la ruta del directorio de salida
    skeleton_dir = get_skeleton_path("")
    
    templates_dir = get_templates_path("compose")
    
      # Leo la plantilla de dockerfile para el frontend
    template_compose = read_template(templates_dir,'docker-compose.yml' );

    write_artefact(skeleton_dir, 'docker-compose.yml',template_compose);
    
    
    # Leo la plantilla de .env 
    templates_dir = get_templates_path("..")
    template_compose = read_template(templates_dir,'.env' );

    write_artefact(skeleton_dir, '.env',template_compose);

def apply_transformations(model):
    """
    Aplica las transformaciones al modelo dado.
    :param model: El modelo al que se aplicarán las transformaciones.
    :return: None
    """
    
    # Componentes del modelo por tipo
    components = {
        "frontend": [],
        "api_gateway": [],
        "load_balancer": [],
        "backend": [],
        "database": []
    }

    connectors = []

    # Obtener los Componentes del modelo por tipo
    for element in model.elements:
        if element.__class__.__name__ == "Component":
            components[element.type].append(element)
        elif element.__class__.__name__ == "Connector":
            connectors.append(element)
            
    # Aplicar transformaciones a cada componente
    for component_type, elements in components.items():
        if component_type == "frontend":
            # Aplicar transformaciones específicas para frontend
            for element in elements:
                generate_frontend(element)
        elif component_type == "api_gateway":
            # Aplicar transformaciones específicas para api_gateway
            for element in elements:
                generate_api_gateway(element)
        elif component_type == "load_balancer":
            # Aplicar transformaciones específicas para load_balancer
            # Esta logica se debe crear por aparte cuando se tengan creadas
            # las instancias del backend o frontend
            for element in elements:
                loadBalancerTargets = get_load_balancer_targets(element, connectors)
                generate_load_balancer(element, loadBalancerTargets)
        elif component_type == "backend":
            # Aplicar transformaciones específicas para backend
            for element in elements:
                # Aquí se puede agregar la lógica para generar el backend
                generate_backend(element)
        elif component_type == "database":
            # Aplicar transformaciones específicas para database
            for element in elements:
                # Aquí se puede agregar la lógica para generar la base de datos
                generate_database(element)
    generate_docker_compose()

### Helper functions ###
def get_templates_path(element_name):
    """
    Determina la ruta de las plantillas para el elemento dado teniendo en cuenta si se está ejecutando en un contenedor o localmente.
    :param element_name: El elemento del modelo del cual se requiere la ruta.
    :return: None
    """
    # Si el directorio /app existe, el proyecto se está ejecutando en el contenedor
    app_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app"))
    app_dir_exists = os.path.exists(app_dir)

    if app_dir_exists:
        return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app", "templates", element_name))
    else:
        # Esta opción soporta la ejecución local del proyecto
        return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src", "templates", element_name))
    
def get_skeleton_path(element_name):
    """
    Determina la ruta de las plantillas para el elemento dado teniendo en cuenta si se está ejecutando en un contenedor o localmente.
    :param element_name: El elemento del modelo del cual se requiere la ruta.
    :return: None
    """
    # Si el directorio /app existe, el proyecto se está ejecutando en el contenedor
    app_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app"))
    app_dir_exists = os.path.exists(app_dir)

    if app_dir_exists:
        return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app", "skeleton", element_name))
    else:
        # Esta opción soporta la ejecución local del proyecto
        return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src", "skeleton", element_name))
    
def get_load_balancer_targets(element, connectors):
    """
    Obtiene los targets del Load Balancer a partir de los elementos conectados.
    :param element: El elemento del modelo que representa el Load Balancer.
    :param connectors: Los conectores del modelo.
    :return: None
    """
    targets = []
    for connector in connectors:
        # Debemos usar la función getattr para obtener el valor del atributo "from" del conector
        # ya que "from" es una palabra reservada en Python
        connectionSource = getattr(connector, "from").name
        if connectionSource == element.name:
            targets.append(connector.to.name)
    return targets

def replace_placeholders(template, placeholders):
    """
    Reemplaza los marcadores de posición en la plantilla con los valores dados.
    :param template: La plantilla en la que se reemplazarán los marcadores de posición.
    :param placeholders: Un diccionario con los marcadores de posición y sus valores correspondientes.
    :return: La plantilla con los marcadores de posición reemplazados.
    """
    for placeholder, value in placeholders.items():
        template = template.replace(placeholder, value)
    return template


def write_artefact(directory, name_file, content):
    """Escribe un artefacto en un archivo.

    Args:
        directory (str): Directorio donde se guardará el archivo.
        name_file (str): Nombre del archivo a guardar.
        content (str): Contenido que se escribirá en el archivo.
    """
    try:
        path =os.path.join(directory, name_file)
        # Crear el directorio si no existe
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            f.write(content)
    except OSError as e:
        logging.error(f"Error al escribir el archivo en {path}: {e}")
        
        
def read_template(directory, template_name):
    """Lee un archivo desde el disco
    
    Args:
        directoriy: Directorio especifico para leer el archivo
        template_name: Nombre del archivo a leer
    """
        # Obtener la ruta del directorio de plantillas
    
    template_path = os.path.join(directory,  template_name)
    if not os.path.exists(template_path):
        logging.warning(f"El archivo de plantilla no existe: {template_path}")
        return ""
    with open(template_path, 'r') as f:
        return f.read()
