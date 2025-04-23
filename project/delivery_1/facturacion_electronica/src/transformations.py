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
    templates_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "templates", name))

    # Obtener la ruta del directorio de salida
    skeleton_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "skeleton", name))

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
    templates_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "templates", name))

    # Obtener la ruta del directorio de salida
    skeleton_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "skeleton", name))

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


def generate_load_balancer(element, instances):
    """
    Genera el Load Balancer para la aplicación usando las plantillas.
    :param element: El elemento del modelo que representa el Load Balancer.
    :return: None
    """
    # Obtener el nombre del Load Balancer
    name = element.name[:-1]

    # Obtener la ruta del directorio de plantillas
    templates_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "templates", name))

    # Obtener la ruta del directorio de salida
    skeleton_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "skeleton", name))

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
    # Usar las instancias del backend o frontend
    # template = template.replace("{{MARCADOR}}", VALOR)
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
    templates_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "templates", name))

    # Obtener la ruta del directorio de salida
    skeleton_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "skeleton", name))

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
    templates_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "templates", name))

    # Obtener la ruta del directorio de salida
    skeleton_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "skeleton", name))

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
    
    # Obtener los Componentes del modelo por tipo
    for element in model.elements:
        if element.type in components:
            components[element.type].append(element)
    
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
                generate_load_balancer(element, [])
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
