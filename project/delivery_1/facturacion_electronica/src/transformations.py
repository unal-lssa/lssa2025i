import logging
import os

from dotenv import load_dotenv

load_dotenv()  # take environment variables

# Configurar el nivel de logging
logging.basicConfig(level=logging.DEBUG)

def generate_api_gateway(element):
    """
    Genera el API Gateway para la aplicación usando las plantillas.
    :param element: El elemento del modelo que representa el api_gateway.
    :return: None
    """
    # Obtener el nombre del api_gateway
    name = element.name

    # Obtener la ruta del directorio de plantillas
    templates_dir = get_templates_path(name)

    # Obtener la ruta del directorio de salida
    skeleton_dir = get_skeleton_path(name)

    # Existen 3 archivos de plantilla para el frontend
    # 1. app.py
    # 2. Dockerfile
    # 3. requirements.txt

    # Generar los archivos de plantilla
    # 1. app.py
    template_path = os.path.join(templates_dir, "app.py")
    with open(template_path, "r") as template_file:
        template = template_file.read()
    # Guardar el archivo generado
    with open(os.path.join(skeleton_dir, "app.py"), "w") as output_file:
        output_file.write(template)

    # 2. Dockerfile
    template_path = os.path.join(templates_dir, "Dockerfile")
    with open(template_path, "r") as template_file:
        template = template_file.read()
    # Guardar el archivo generado
    with open(os.path.join(skeleton_dir, "Dockerfile"), "w") as output_file:
        output_file.write(template)

    # 3. requirements.txt
    template_path = os.path.join(templates_dir, "requirements.txt")
    if os.path.exists(template_path):
        with open(template_path, "r") as template_file:
            template = template_file.read()
        # Guardar el archivo generado
        with open(os.path.join(skeleton_dir, "requirements.txt"), "w") as output_file:
            output_file.write(template)


def generate_load_balancer(element, target):
    """
    Genera el Load Balancer para la aplicación usando las plantillas.
    :param element: El elemento del modelo que representa el Load Balancer.
    :param target: El elemento del modelo que representa el Backend.
    :return: None
    """
    # Obtener el nombre del Load Balancer
    name = element.name

    # Obtener la ruta del directorio de plantillas
    templates_dir = get_templates_path(name)

    # Obtener la ruta del directorio de salida
    skeleton_dir = get_skeleton_path(name)

    # Existen 2 archivos de plantilla para el Load Balancer
    # 1. nginx.conf
    # 2. Dockerfile

    # Generar los archivos de plantilla
    # 1. nginx.conf
    template_path = os.path.join(templates_dir, "nginx.conf")
    with open(template_path, "r") as template_file:
        template = template_file.read()
    # Reemplazar los marcadores de posición en la plantilla
    VALOR = "server " + str(target["name"]) + ":" + str(target["port"]) + ";"
    template = template.replace("###Targets###", VALOR)

    # Guardar el archivo generado
    with open(os.path.join(skeleton_dir, "nginx.conf"), "w") as output_file:
        output_file.write(template)

    # 2. Dockerfile
    template_path = os.path.join(templates_dir, "Dockerfile")
    with open(template_path, "r") as template_file:
        template = template_file.read()
    # Guardar el archivo generado
    with open(os.path.join(skeleton_dir, "Dockerfile"), "w") as output_file:
        output_file.write(template)


def generate_microservice(element):
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
    
    # Generar los archivos de plantilla
    template_path = os.path.join(templates_dir)
    if os.path.exists(templates_dir):
        for file_name in os.listdir(templates_dir):
            template_path = os.path.join(templates_dir, file_name)
            if os.path.isfile(template_path):
                with open(template_path, "r") as template_file:
                    template = template_file.read()
                # Guardar el archivo generado en el directorio de salida
                output_path = os.path.join(skeleton_dir, file_name)
                with open(output_path, "w") as output_file:
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
        "database": [],
    }

    # Conectores del modelo
    connectors = []

    # Skeleton de la arquitectura
    # 1. Frontend
    # 2. API Gateway
    # 3. Load Balancer
    # 4. Backend
    # 5. Base de Datos
    # 6. Docker Compose
    # 7. .env
    skeleton = {
        "frontend": [],
        "api_gateway": [],
        "load_balancer": [],
        "backend": [],
        "database": [],
        "docker_compose": "docker-compose.yml",
        ".env": ".env",
    }

    # Obtener los Componentes del modelo por tipo
    for element in model.elements:
        if element.__class__.__name__ == "Component":
            components[element.type].append(element)
        elif element.__class__.__name__ == "Connector":
            connectors.append(element)

    # Aplicar transformaciones a cada componente
    for component_type, elements in components.items():

        if component_type == "frontend" or component_type == "backend":
            # Aplicar transformaciones específicas para frontend
            for element in elements:
                generate_microservice(element)
        elif component_type == "api_gateway":
            # Aplicar transformaciones específicas para api_gateway
            for element in elements:
                generate_api_gateway(element)
                skeleton["api_gateway"].append(
                    {
                        "name": element.name,
                        "port": os.getenv("API_GATEWAY_PORT", 5003),
                        "instances": 1 if element.instances < 1 else element.instances,
                    }
                )

        elif component_type == "load_balancer":
            # Aplicar transformaciones específicas para load_balancer
            for element in elements:
                target = get_load_balancer_target(element, connectors)
                generate_load_balancer(element, target)
                skeleton["load_balancer"].append(
                    {
                        "name": target["name"],
                        "port": target["port"],
                        "instances": (
                            1 if target["instances"] < 1 else target["instances"]
                        ),
                    }
                )
        elif component_type == "database":
            # Aplicar transformaciones específicas para database
            for element in elements:
                # Aquí se puede agregar la lógica para generar la base de datos
                generate_database(element)
                skeleton["database"].append(
                    {
                        "name": element.name,
                        "port": 3306,
                        "instances": 1 if element.instances < 1 else element.instances,
                    }
                )

    # Generar el docker compose
    generate_docker_compose(skeleton)


### Helper functions ###
def get_templates_path(element_name: str) -> str:
    """
    Obtiene la ruta de las plantillas para el elemento dado.
    :param element_name: El nombre del elemento del modelo el cual se requiere para la ruta de las plantillas.
    :return: str
    """
    templates_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "templates", element_name)
    )
    # Si no existe el directorio de plantillas, se imprime un mensaje de error y se aborata la ejecución
    if not os.path.exists(templates_dir):
        logging.error(f"El directorio de plantillas no existe: {templates_dir}")
        raise FileNotFoundError(
            f"El directorio de plantillas no existe: {templates_dir}"
        )
    return templates_dir


def get_skeleton_path(element_name: str) -> str:
    """
    Obtiene la ruta donde sera guardado el esqueleto para el elemento dado.
    :param element_name: El nombre del elemento del modelo el cual se requiere para la ruta del esqueleto.
    :return: str
    """
    skeleton_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "skeleton", element_name)
    )
    # Crear el directorio de salida si no existe
    if not os.path.exists(skeleton_dir):
        os.makedirs(skeleton_dir)
    return skeleton_dir


def get_load_balancer_target(element, connectors):
    """
    Obtiene el target del Load Balancer, la cantidad de instancias y el puerto del target.
    :param element: El elemento del modelo que representa el Load Balancer.
    :param connectors: Los conectores del modelo.
    :return: dict
    """
    # Obtener el target del Load Balancer
    target = list(
        filter(
            lambda conn: conn.type == "lb_conn"
            and getattr(conn, "from").name == element.name,
            connectors,
        )
    )[0].to
    # Obtener la cantidad de instancias del target y el puerto del target
    target = {
        "name": target.name,
        "port": get_backend_ports(target.name)
    }
    return target


def get_backend_ports(backend_name):
    """
    Obtiene el puerto del backend dado su nombre.
    :param backend_name: El nombre del backend.
    :return: int
    """
    return {
        "users_be": os.getenv("USERS_BACKEND_PORT", 5007),
        "efact_writing_be": os.getenv("EFACT_READING_BACKEND_PORT", 5008),
        "efact_reading_be": os.getenv("EFACT_WRITING_BACKEND_PORT", 5009),
        "auth_be": os.getenv("AUTH_BACKEND_PORT", 5010),
    }[backend_name]


def get_frontend_ports(frontend_name):
    """
    Obtiene el puerto del frontend dado su nombre.
    :param frontend_name: El nombre del frontend.
    :return: int
    """
    return {
        "register_fe": os.getenv("REGISTER_FRONTEND_PORT", 5001),
        "seller_fe": os.getenv("SELLER_FRONTEND_PORT", 5002),
        "admin_fe": os.getenv("ADMIN_FRONTEND_PORT", 5003),
    }[frontend_name]


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
        path = os.path.join(directory, name_file)
        # Crear el directorio si no existe
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
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

    template_path = os.path.join(directory, template_name)
    if not os.path.exists(template_path):
        logging.warning(f"El archivo de plantilla no existe: {template_path}")
        return ""
    with open(template_path, "r") as f:
        return f.read()
