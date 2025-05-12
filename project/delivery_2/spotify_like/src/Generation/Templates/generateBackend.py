import os

from DSL.AComponent import AComponent
from DSL.ApiGateway import ApiGateway
from DSL.Database import Database
from DSL.Connector import Connector
from DSL.LoadBalancer import LoadBalancer
from DSL.Queue import Queue
from DSL.StandardComponent import StandardComponent, StandardComponentType

from Generation.NetworkOrchestrator import NetworkOrchestrator

# ---
# [X] Imports
# ---
# [X] Setup Redis (Si usa cache)
# ---
# [X] Setup Database (Si usa DB)
# ---
# [ ] Setup Queue (Si usa Queue)
# ---
# [X] Setup Flask
# ---
# [X] Codigo Limit Exposure API Gateway
# ---
# [X] Codigo servicio Auth (Usar cache o db)
# [ ] Codigo servicio Producer Queue (Usar cache o db)
# [ ] Codigo servicio Consumer Queue (Usar cache o db)
# [ ] Codigo servicio General (Usar cache o db)
# ---
# [X] Codigo execute flask serice (port)


def _get_connected_componentes(
    comp: AComponent, conn_list: list[Connector]
) -> dict[str, dict[str, list[AComponent]]]:
    components = {
        "from": {
            "database": [],
            "queue": [],
            "cache": [],
            "api_gateway": [],
            "load_balancer": [],
            "service": [],
        },
        "to": {
            "database": [],
            "queue": [],
            "cache": [],
            "api_gateway": [],
            "load_balancer": [],
            "service": [],
        },
    }

    for conn in conn_list:
        if conn.from_comp.name == comp.name:
            if isinstance(conn.to_comp, Database):
                components["from"]["database"].append(conn.to_comp)
            elif isinstance(conn.to_comp, Queue):
                components["from"]["queue"].append(conn.to_comp)
            elif (
                isinstance(conn.to_comp, StandardComponent)
                and conn.to_comp.type == StandardComponentType.CACHE
            ):
                components["from"]["cache"].append(conn.to_comp)
            else:
                components["from"]["service"].append(conn.to_comp)
        elif conn.to_comp.name == comp.name:
            if isinstance(conn.from_comp, ApiGateway):
                components["to"]["api_gateway"].append(conn.from_comp)
            elif isinstance(conn.from_comp, LoadBalancer):
                components["to"]["load_balancer"].append(conn.from_comp)
            else:
                components["to"]["service"].append(conn.from_comp)
    return components


def get_import_dependencies(comp: AComponent, conn_list: list[Connector]):
    conn_map = _get_connected_componentes(comp, conn_list)

    dependencies = set()
    dependencies.add("flask")
    dependencies.add("pyjwt")

    # Add dependencies based on connected components
    ## Database
    if conn_map["from"]["database"]:
        for db in conn_map["from"]["database"]:
            match db.database_type.value:
                case "postgresql":
                    dependencies.add("psycopg2-binary")
                case "mysql":
                    dependencies.add("mysql-connector-python")
                case "mongodb":
                    dependencies.add("pymongo")
                case "elasticsearch":
                    dependencies.add("elasticsearch")
                case _:
                    raise ValueError(f"Unknown database type: {db.database_type}")
    ## Queue
    if conn_map["from"]["queue"]:
        dependencies.add("pika")
    ## Cache
    if conn_map["from"]["cache"]:
        dependencies.add("redis")
    ## Query other services
    if (
        conn_map["to"]["api_gateway"]
        or conn_map["to"]["load_balancer"]
        or conn_map["to"]["service"]
    ):
        dependencies.add("requests")

    return list(dependencies)


def _get_imports_lines(dependencies: list):
    lines = []
    lines.append("import datetime")
    for dep in dependencies:
        match dep:
            case "flask":
                lines.append("from flask import Flask, jsonify, request")
            case "psycopg2-binary":
                lines.append("import psycopg2")
                lines.append("from psycopg2.extras import RealDictCursor")
            case "mysql-connector-python":
                lines.append("import mysql.connector")
            case "pymongo":
                lines.append("from pymongo import MongoClient")
            case "elasticsearch":
                lines.append("from elasticsearch import Elasticsearch")
            case "pika":
                lines.append("import pika")
            case "redis":
                lines.append("import redis")
            case "requests":
                lines.append("import requests")
            case "pyjwt":
                lines.append("import jwt")
            case _:
                pass
    return "\n".join(lines)


def _get_cache_setup_lines(cache_comp: AComponent, net_orch: NetworkOrchestrator):
    if (
        not isinstance(cache_comp, StandardComponent)
        or not cache_comp.type == StandardComponentType.CACHE
    ):
        return None

    lines = []
    lines.append(
        f"cache_{cache_comp.name} = redis.Redis(host='{cache_comp.name}', port={net_orch.get_assigned_port(cache_comp)}, db=0)"
    )
    lines.append("cache.ping()")
    lines.append(f"print('Connected to Redis cache {cache_comp.name}')")
    return "\n".join(lines)


def _get_database_setup_lines(db_comp: AComponent, net_orch: NetworkOrchestrator):
    if not isinstance(db_comp, Database):
        return None

    lines = []
    host = database_name = db_comp.name
    port = net_orch.get_assigned_port(db_comp)
    user = "admin"
    password = "admin"
    match db_comp.database_type.value:
        case "postgresql":
            lines.append(
                f"conn_{db_comp.name} = psycopg2.connect(host='{host}', port={port}, user='{user}', password='{password}', dbname='{database_name}')"
            )
            lines.append(
                f"cursor_{db_comp.name} = conn_{db_comp.name}.cursor(cursor_factory=RealDictCursor)"
            )
        case "mysql":
            lines.append(
                f"conn_{db_comp.name} = mysql.connector.connect(host='{host}', port={port}, user='{user}', password='{password}', database='{database_name}')"
            )
        case "mongodb":
            lines.append(
                f"client_{db_comp.name} = MongoClient(host='{host}', port={port}, username='{user}', password='{password}')"
            )
            lines.append(f"db = client['{database_name}']")
        case "elasticsearch":
            lines.append(
                f"es_{db_comp.name} = Elasticsearch([{{'host': '{host}', 'port': {port}}}], http_auth=('{user}', '{password}'))"
            )
        case _:
            raise ValueError(f"Unknown database type: {db_comp.database_type}")

    lines.append(
        f"print('Connected to database {db_comp.name} with type {db_comp.database_type}')"
    )
    return "\n".join(lines)


def _get_flask_app_setup_lines(comp: AComponent, net_orch: NetworkOrchestrator):
    lines = []
    lines.append("app = Flask(__name__)")
    lines.append(f"app.config['SECRET_KEY'] = 'your_secret_key'")

    return "\n".join(lines)


def _get_token_required_decorator_lines():
    lines = []
    lines.append("def token_required(f):")
    lines.append("    from functools import wraps")
    lines.append("    @wraps(f)")
    lines.append("    def decorated_function(*args, **kwargs):")
    lines.append("        token = request.headers.get('Authorization')")

    lines.append("        if not token:")
    lines.append("            return jsonify({'message': 'Token is missing!'}), 403")

    lines.append("        try:")
    lines.append(
        "            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])"
    )
    lines.append("        except jwt.ExpiredSignatureError:")
    lines.append("            return jsonify({'message': 'Token has expired!'}), 403")
    lines.append("        except jwt.InvalidTokenError:")
    lines.append("            return jsonify({'message': 'Invalid token!'}), 403")

    lines.append("        return f(*args, **kwargs)")
    lines.append("    return decorated_function")

    return "\n".join(lines)


def _get_limit_exposure_decorator_lines(source: str = "api-gateway"):
    lines = []
    lines.append("def limit_exposure(f):")
    lines.append("    from functools import wraps")
    lines.append("    import socket")
    lines.append("    @wraps(f)")
    lines.append("    def decorated_function(*args, **kwargs):")
    lines.append("        client_ip = request.remote_addr")
    lines.append("        try:")
    lines.append(f"            AUTHORIZED_IP = socket.gethostbyname('{source}')")
    lines.append("        except socket.gaierror:")
    lines.append("            AUTHORIZED_IP = None")
    lines.append(
        f"            print(\"Error: Unable to resolve '{source}' to an IP address\")"
    )
    lines.append("        if AUTHORIZED_IP is None:")
    lines.append(
        "            return jsonify({'message': 'Forbidden: Unauthorized IP'}), 403"
    )
    lines.append("        if client_ip == AUTHORIZED_IP:")
    lines.append("            return f(*args, **kwargs)")
    lines.append("        elif client_ip == 'localhost':")
    lines.append("            return f(*args, **kwargs)")
    lines.append("        else:")
    lines.append(
        "            return jsonify({'message': 'Forbidden: Unauthorized IP'}), 403"
    )
    lines.append("    return decorated_function")

    return "\n".join(lines)


def write_docker_file(output_dir: str, dependencies: list):
    with open(os.path.join(output_dir, "requirements.txt"), "w") as f:
        f.write("\n".join(dependencies))

    with open(os.path.join(output_dir, "Dockerfile"), "w") as f:
        f.write("FROM python:3.11-slim\n")
        f.write("WORKDIR /app\n")
        f.write("COPY . .\n")
        f.write("RUN pip install -r requirements.txt\n")
        f.write('CMD ["python", "app.py"]\n')


def _get_base_service_lines(
    comp: AComponent, conn_list: list[Connector], net_orch: NetworkOrchestrator
):
    conn_map = _get_connected_componentes(comp, conn_list)
    dependencies = get_import_dependencies(comp, conn_list)

    lines = []
    lines.append(_get_imports_lines(dependencies))

    for cache in conn_map["from"]["cache"]:
        lines.append(_get_cache_setup_lines(cache, net_orch))
    for db in conn_map["from"]["database"]:
        lines.append(_get_database_setup_lines(db, net_orch))

    source = None
    if len(conn_map["to"]["api_gateway"]) > 0:
        source = conn_map["to"]["api_gateway"][0].name
    elif len(conn_map["to"]["load_balancer"]) > 0:
        source = conn_map["to"]["load_balancer"][0].name
    elif len(conn_map["to"]["service"]) > 0:
        source = conn_map["to"]["service"][0].name

    lines.append(_get_flask_app_setup_lines(comp, net_orch))
    lines.append(_get_token_required_decorator_lines())
    lines.append(_get_limit_exposure_decorator_lines(source=source or "api-gateway"))

    return lines


def _get_query_user_lines(database: Database, ident_space: int = 0):
    lines = []

    match database.database_type.value:
        case "postgresql":
            lines.append(
                f"cursor_{database.name}.execute('SELECT * FROM users WHERE username = %s', (username,))"
            )
            lines.append(f"user = cursor_{database.name}.fetchone()")
        case "mysql":
            lines.append(
                f"cursor_{database.name}.execute('SELECT * FROM users WHERE username = %s', (username,))"
            )
            lines.append(f"user = cursor_{database.name}.fetchone()")
        case "mongodb":
            lines.append(f"user = db['users'].find_one({{'username': username}})")
        case "elasticsearch":
            raise NotImplementedError("Elasticsearch query not implemented yet.")
        case _:
            raise ValueError(f"Unknown database type: {database.database_type}")

    # Consider identation
    prefix = "    " * ident_space
    for i in range(len(lines)):
        lines[i] = prefix + lines[i]
    return lines


def _get_example_protected_endpoint_lines():
    lines = []
    lines.append("@app.route('/protected', methods=['GET'])")
    lines.append("@token_required")
    lines.append("@limit_exposure()")
    lines.append("def protected():")
    lines.append("    return jsonify({'message': 'This is a protected route'})")
    return "\n".join(lines)


def get_auth_service_lines(
    comp: AComponent, conn_list: list[Connector], net_orch: NetworkOrchestrator
):
    conn_map = _get_connected_componentes(comp, conn_list)

    db = None
    cache = None
    if len(conn_map["from"]["database"]) > 0:
        db = conn_map["from"]["database"][0]
    if len(conn_map["from"]["cache"]) > 0:
        cache = conn_map["from"]["cache"][0]

    lines = _get_base_service_lines(comp, conn_list, net_orch)

    lines.append("TOKEN_EXPIRATION_SECONDS = 3600")

    lines.append("@app.route('/login', methods=['POST'])")
    lines.append("@limit_exposure()")
    lines.append("def login():")
    lines.append("    auth = request.get_json() or {}")
    lines.append("    username = auth.get('username')")
    lines.append("    password = auth.get('password')")

    if cache:
        lines.append(f"    cache = cache_{cache.name}")
        lines.append("    cached_user = cache.hgetall(username)")
        lines.append(
            "    if cached_user and cached_user.get(b'password') == password.encode():"
        )
        lines.append(
            "        token = jwt.encode({'username': username,"
            + "'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=TOKEN_EXPIRATION_SECONDS)},"
            + "app.config['SECRET_KEY'], algorithm='HS256')"
        )
        lines.append("        return jsonify({'token': token}), 200")

    if db:
        # Consider identation
        lines.extend(_get_query_user_lines(db, ident_space=1))
        lines.append("    if user and user['password'] == password:")
        lines.append(
            "        token = jwt.encode({'username': username,"
            + "'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=TOKEN_EXPIRATION_SECONDS)},"
            + "app.config['SECRET_KEY'], algorithm='HS256')"
        )
        lines.append("        return jsonify({'token': token}), 200")
        lines.append("    return jsonify({'message': 'Invalid credentials'}), 401")

    _get_example_protected_endpoint_lines()

    lines.append("if __name__ == '__main__':")
    lines.append(
        f"    app.run(host='0.0.0.0', port={net_orch.get_assigned_port(comp)}, debug=True)"
    )
    return "\n".join(lines)
