from .database.generate_database import generate_database
from .backend.generate_backend import generate_backend
from .frontend.generate_frontend import generate_frontend
from .load_balancer.generate_load_balancer import generate_loadbalancer
from .compose.generate_docker_compose import generate_docker_compose
from .api_gateway.generate_api_gateway import generate_api_gateway
from .cdn.generate_cdn import generate_cdn
from .bucket.generate_bucket import generate_bucket, move_file
import os


def process_connectors(model):
    """
    Procesa todos los conectores en el modelo y devuelve un diccionario donde la llave
    es el nombre de un componente, y el valor es otro diccionario con dos listas:
    'outgoing' para conexiones salientes y 'incoming' para conexiones entrantes.
    Cada elemento en estas listas es un diccionario describiendo la conexión
    (tipo, y el otro componente involucrado - target para salientes, source para entrantes).
    """
    component_connections = {}

    # Inicializar cada componente en el diccionario principal
    # Esto asegura que incluso los componentes sin conexiones aparezcan con listas vacías
    for element in model.elements:
        # Solo nos interesan los Elements que son Componentes
        if element.__class__.__name__ in [
            "LoadBalancer",
            "StandardComponent",
            "Database",
            "ApiGateway",
        ]:
            component_name = element.name
            if component_name not in component_connections:
                component_connections[component_name] = {"outgoing": [], "incoming": []}

    # Procesar los conectores
    for element in model.elements:
        if element.__class__.__name__ == "Connector":
            # Usa getattr para evitar el problema con la palabra reservada 'from'
            source_component_name = getattr(element, "from").name
            target_component_name = element.to.name
            conn_type = element.type

            # Asegurarse de que los componentes existan en el diccionario,
            # aunque ya los inicializamos antes, esto es una doble verificación útil.
            if source_component_name not in component_connections:
                component_connections[source_component_name] = {
                    "outgoing": [],
                    "incoming": [],
                }
            if target_component_name not in component_connections:
                component_connections[target_component_name] = {
                    "outgoing": [],
                    "incoming": [],
                }

            # Agregar la conexión saliente para el componente fuente
            component_connections[source_component_name]["outgoing"].append(
                {"type": conn_type, "target": target_component_name}
            )

            # Agregar la conexión entrante para el componente destino
            component_connections[target_component_name]["incoming"].append(
                {"type": conn_type, "source": source_component_name}
            )

    return component_connections


def extract_architecture_data(model):
    """
    Extrae información estructurada del modelo de arquitectura.

    Organiza la información de componentes, sus detalles específicos y
    las conexiones en un único diccionario para facilitar su uso posterior.

    Args:
        model: El modelo de arquitectura parseado por textx.

    Returns:
        Un diccionario con la siguiente estructura:
        {
            'components': {
                'nombre_componente': {
                    'type': 'tipo_string', # ej: 'frontend', 'db', 'loadbalancer'
                    'details': { ... } # Detalles específicos del tipo de componente
                },
                ...
            },
            'connections': { # Resultado de process_connectors mejorada
                'nombre_componente': {
                    'outgoing': [{...}],
                    'incoming': [{...}]
                },
                ...
            },
            'replicas': { # Mapeo de componente target de LB a count
                 'nombre_componente_target': cantidad_instancias,
                 ...
            }
        }
    """
    architecture_data = {
        "components": {},
        "connections": {},  # Esto se llenará llamando a process_connectors
        "replicas": {},
    }

    # Primera pasada: Identificar todos los componentes y sus detalles estáticos
    for element in model.elements:
        # Verificamos si es alguno de los tipos de Componente definidos
        if element.__class__.__name__ in [
            "StandardComponent",
            "Database",
            "LoadBalancer",
            "ApiGateway",
        ]:
            component_name = element.name
            component_type = None
            details = {}

            if element.__class__.__name__ == "StandardComponent":
                component_type = element.type  # frontend, backend, bucket, cdn, queue
            elif element.__class__.__name__ == "Database":
                component_type = "db"
                details["databaseType"] = element.databaseType
            elif element.__class__.__name__ == "LoadBalancer":
                component_type = "loadbalancer"
                details["instanceCount"] = element.instanceCount
                # Almacenamos el nombre del componente target
                if hasattr(element, "target") and element.target:
                    details["target"] = element.target.name
            elif element.__class__.__name__ == "ApiGateway":
                component_type = "api_gateway"
                # Almacenamos el nombre del componente de autenticación
                if hasattr(element, "auth") and element.auth:
                    details["auth"] = element.auth.name

            # Guardar la información básica del componente
            architecture_data["components"][component_name] = {
                "type": component_type,
                "details": details,
            }

    # Segunda parte: Procesar las conexiones usando la función mejorada
    # Esta función ya maneja la estructura 'outgoing'/'incoming'
    architecture_data["connections"] = process_connectors(model)

    # Tercera parte: Extraer la información de réplicas de los LoadBalancers
    # Iteramos sobre los componentes que ya identificamos
    for component_name, component_info in architecture_data["components"].items():
        if component_info["type"] == "loadbalancer":
            details = component_info["details"]
            if "target" in details and "instanceCount" in details:
                target_name = details["target"]
                instance_count = details["instanceCount"]
                # La cantidad de réplicas se asocia al componente target
                architecture_data["replicas"][target_name] = instance_count

    return architecture_data


def generate_architecture(architecture):
    """
    Genera los componentes de la arquitectura (bases de datos, backends, frontends, etc.)
    basándose en el diccionario de arquitectura proporcionado en el nuevo formato JSON.

    Args:
        architecture: Un diccionario que contiene las claves 'components', 'connections' y 'replicas'.
                      Este diccionario es el resultado de la función extract_architecture_data.

    Nota: Las funciones 'generate_...' son llamadas dentro de esta función
    y se espera que manejen la creación de los artefactos de salida.
    """
    components_data = architecture.get("components", {})
    connections_data = architecture.get("connections", {})
    replicas_data = architecture.get("replicas", {})

    # --- Pre-procesar datos para identificar productores y rutas de API Gateway ---

    # Identificar backends que son productores (conexión saliente a una cola)
    # Basado en la interpretación estándar: un productor envía a la cola.
    consumer_backends_derived = set()
    source_backends_map = {}  # Mapeo de backends a sus fuentes
    for comp_name, comp_conn in connections_data.items():
        for incoming_conn in comp_conn.get("incoming", []):
            conn_type = incoming_conn.get("type")
            source_name = incoming_conn.get("source")
            if source_name:
                source_comp_data = components_data.get(source_name)
                # Si el objetivo es una cola y el tipo de conexión es apropiado
                if (
                    source_comp_data
                    and source_comp_data.get("type") == "queue"
                    and conn_type in ["kafka_connector", "queue_connector"]
                ):
                    consumer_backends_derived.add(
                        comp_name
                    )  # Este componente es un consumidor
                    source_backends_map[comp_name] = (
                        source_name  # Mapeo de origen a destino
                    )

    producer_backends = set()  # Conjuntos de backends productores
    producer_backends_map = {}  # Mapeo de backends a sus productores
    for comp_name, comp_conn in connections_data.items():
        for incoming_conn in comp_conn.get("outgoing", []):
            if incoming_conn.get("type") != "kafka_connector":
                continue
            target_name = incoming_conn.get("target")
            if target_name and target_name in components_data:
                target_comp_data = components_data.get(target_name)
                if target_comp_data and target_comp_data.get("type") == "queue":
                    producer_backends.add(comp_name)
                    producer_backends_map[comp_name] = target_name

    # Preparar el mapa de rutas para los API Gateways
    api_gateway_routes = {}  # {gateway_name: {target: target, ...}}
    for comp_name, comp_data in components_data.items():
        if comp_data.get("type") == "api_gateway":
            # Buscar conexiones salientes HTTP para este API Gateway
            comp_conn = connections_data.get(comp_name, {})
            route_map = {}
            for outgoing_conn in comp_conn.get("outgoing", []):
                if outgoing_conn.get("type") == "http" and outgoing_conn.get("target"):
                    target_name = outgoing_conn.get("target")
                    route_map[target_name] = target_name  # Mapeo target a target
            api_gateway_routes[comp_name] = route_map

    # print("API Gateway routes:", api_gateway_routes) # Para depuración

    # Iterar sobre cada componente definido en el diccionario de arquitectura
    for name, comp_data in components_data.items():
        comp_type = comp_data.get("type")
        details = comp_data.get("details", {})
        # Obtener las conexiones específicas para este componente
        component_connections = connections_data.get(
            name, {}
        )  # Estructura {outgoing: [...], incoming: [...]}

        # Manejar diferentes tipos de componentes
        if comp_type in ["database", "db"]:
            db_type = details.get("databaseType", "mysql")
            generate_database(name, db_type)

        elif comp_type == "backend":
            backend_db_type = "mysql"  # valor por defecto
            connected_db_name = None  # Nombre de la BD conectada

            # Encontrar detalles de conexión a BD en las conexiones salientes
            for outgoing_conn in component_connections.get("outgoing", []):
                if outgoing_conn.get("type") == "db_connector" and outgoing_conn.get(
                    "target"
                ):
                    connected_db_name = outgoing_conn.get("target")
                    # Obtener el tipo de la BD conectada desde sus detalles de componente
                    db_comp_data = components_data.get(connected_db_name)
                    if db_comp_data and db_comp_data.get("type") in ["database", "db"]:
                        backend_db_type = db_comp_data.get("details", {}).get(
                            "databaseType", "mysql"
                        )
                    break  # Asumiendo solo una conexión saliente db_connector por backend

            # Verificar si este backend es un productor (usando el conjunto derivado)
            if name in consumer_backends_derived:
                # Replicar la estructura de conexiones específica del fragmento original para productores
                generate_backend(
                    name,
                    connections={"kafka_connector_reverse": source_backends_map[name]},
                )
            elif name in producer_backends:
                # Replicar la estructura de conexiones específica del fragmento original para productores
                generate_backend(
                    name,
                    connections={"kafka_connector": producer_backends_map[name]},
                )
            else:
                # Backend no productor
                # Pasar el nombre de la BD conectada, su tipo, y las conexiones completas del componente.
                generate_backend(
                    name,
                    database=connected_db_name,  # Nombre de la BD conectada si se encuentra
                    database_type=backend_db_type,
                    connections=component_connections,  # Estructura {outgoing: [...], incoming: [...]}
                )

        elif comp_type == "frontend":
            api_gateway_target_name = None
            # Buscar la conexión saliente del frontend que apunte a un API Gateway.
            # Se asume que 'component_connections' contiene las conexiones para el componente actual.
            # Se asume que 'components_data' contiene los datos de todos los componentes para buscar por nombre.
            for outgoing_conn in component_connections.get("outgoing", []):
                target_name = outgoing_conn.get("target")
                if target_name:
                    # Verificar si el componente objetivo existe y es de tipo 'api_gateway'.
                    target_comp_data = components_data.get(target_name)
                    if (
                        target_comp_data
                        and target_comp_data.get("type") == "api_gateway"
                    ):
                        api_gateway_target_name = target_name
                        break  # Encontrado el API Gateway, detener la búsqueda.

            # Llamar a la función generate_frontend con solo el nombre del frontend
            # y el nombre del API Gateway, como se especificó.
            # Se asume que la función generate_frontend tiene la firma generate_frontend(nombre_frontend, nombre_api_gateway).
            # Se pasa el nombre del API Gateway encontrado (o None si no se encontró uno).
            generate_frontend(name, api_gateway_target_name)

        elif comp_type == "cdn":
            generate_cdn(name)

        elif comp_type == "bucket":
            generate_bucket(name)

        # Los tipos 'database', 'loadbalancer', 'api_gateway', 'queue' ahora son manejados
        # como tipos dentro del diccionario 'components', en lugar de clases de elementos de nivel superior.

        elif comp_type == "loadbalancer":
            target_name = details.get("target")
            if target_name:
                # Obtener el conteo de instancias de los detalles (nuevo formato)
                replica_count = details.get("instanceCount", 1)
                # La lógica original usaba el mapa 'replicas_data', pero el nuevo formato
                # tiene 'instanceCount' en los detalles del LB, lo cual es más directo.
                # Si prefieres usar 'replicas_data' como respaldo, sería:
                # replica_count = details.get("instanceCount", replicas_data.get(target_name, 1))

                generate_loadbalancer(name, target_name, replica_count)
            # else: Ignorar si no hay objetivo configurado

        elif comp_type == "api_gateway":
            # Usar el mapa de rutas pre-procesado para este API Gateway
            route_map = api_gateway_routes.get(name, {})

            generate_api_gateway(name, route_map)

        elif comp_type == "queue":
            pass

    generate_docker_compose(architecture)
    src = os.path.join(os.getcwd(), "song.mp3")
    dest = os.path.join(os.getcwd(), "skeleton/music_storage")
    move_file(src, dest)
