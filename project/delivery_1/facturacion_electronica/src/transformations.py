import os


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
    # Obtener el nombre del API Gateway
    name = element.name

    # Obtener la ruta del directorio de plantillas
    templates_dir = get_templates_path(name)

    # Obtener la ruta del directorio de salida
    skeleton_dir = get_skeleton_path(name)

    # Crear el directorio de salida si no existe
    if not os.path.exists(skeleton_dir):
        os.makedirs(skeleton_dir)
    
    # Existen 2 archivos de plantilla para el API Gateway
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