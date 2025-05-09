import os, textwrap
from DSL.Database import Database, DatabaseType
from Generation.NetworkOrchestrator import NetworkOrchestrator

# --- Definición de las estructuras de Queries separadas ---

# Estructura de Query para MySQL
MYSQL_INIT_QUERY = {
    "file_name": "init.sql",
    "content": """
            -- MySQL init query
            CREATE TABLE IF NOT EXISTS systems (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255)
            );
        """,
}

# Estructura de Query por defecto para PostgreSQL
POSTGRESQL_DEFAULT_INIT_QUERY = {
    "file_name": "init.sql",
    "content": """
            -- Default PostgreSQL init query
            CREATE TABLE IF NOT EXISTS generic_data (
                id SERIAL PRIMARY KEY,
                value VARCHAR(255)
            );
        """,
}

# Estructura de Query específica para PostgreSQL de autenticación
POSTGRESQL_AUTH_INIT_QUERY = {
    "file_name": "init.sql",
    "content": """
            -- PostgreSQL auth init query: Base de datos para autenticación
            CREATE TABLE users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL
            );
            -- Índice para búsquedas rápidas por nombre de usuario
            CREATE INDEX idx_users_username ON users (username);
            -- Puedes añadir otras tablas necesarias para autenticación si aplica (ej. roles, permisos)
        """,
}

# Estructura de Query para MongoDB
MONGODB_INIT_QUERY = {
    "file_name": "init-mongo.js",
    "content": """
            // MongoDB init script
            // Se conecta a la base de datos 'admin' para autenticación y luego a la base de datos de la aplicación
            db = db.getSiblingDB('admin');
            // Asumiendo credenciales root/root como en el docker-compose generado
            db.auth('root', 'root');
            // Se conecta a la base de datos nombrada 'app_db' en el script original.
            // Si quisieras usar el nombre 'name' de la BD real, necesitarías pasarlo al script.
            db = db.getSiblingDB('app_db');

            // Ejemplo de creación de colección e inserción
            db.createCollection('systems');
            db.systems.insertOne({ name: 'example_system' });
        """,
}

# Estructura de Query para Elasticsearch
# WARNING: Este script asume que Elasticsearch está corriendo en localhost y el puerto es reemplazado por ##PORT##
ELASTICSEARCH_INIT_QUERY = {
    "file_name": "init-es.sh",
    "content": """
            #!/bin/bash
            # Esperar a que Elasticsearch esté listo (tiempo de espera heurístico)
            sleep 40
            # Crear un índice 'systems' con un mapeo básico.
            # Usar 127.0.0.1 en lugar de localhost para mejor compatibilidad en entornos Docker
            curl -X PUT "127.0.0.1:##PORT##/systems?pretty" -H 'Content-Type: application/json' -d '
            {
                "mappings": {
                   "properties": {
                       "name": { "type": "text" }
                   }
                }
            }
            '
            # Puedes añadir comandos adicionales para crear otros índices o pipelines aquí
        """,
}

# Diccionario para mapear tipos de BD a sus queries por defecto
# Esto simplifica la búsqueda para la mayoría de los casos.
DEFAULT_QUERIES = {
    "mysql": MYSQL_INIT_QUERY,
    "postgresql": POSTGRESQL_DEFAULT_INIT_QUERY,
    "mongodb": MONGODB_INIT_QUERY,
    "elasticsearch": ELASTICSEARCH_INIT_QUERY,
}

# --- Declaración de la función generate_database modificada ---


def generate_database(
    component: Database, net_orch: NetworkOrchestrator, output_dir="skeleton"
):
    path = f"{output_dir}/{component.name}"
    if not os.path.exists(path):
        os.makedirs(path)

    query_data = None

    match component.database_type:
        case DatabaseType.POSTGRESQL:
            if "auth" in component.name.lower():
                query_data = POSTGRESQL_AUTH_INIT_QUERY
            else:
                query_data = DEFAULT_QUERIES.get("postgresql")
        case DatabaseType.MYSQL:
            query_data = DEFAULT_QUERIES.get("mysql")
        case DatabaseType.MONGODB:
            query_data = DEFAULT_QUERIES.get("mongodb")
        case DatabaseType.ELASTICSEARCH:
            query_data = DEFAULT_QUERIES.get("elasticsearch")
            # Reemplazar el puerto en el script de Elasticsearch
            query_data["content"] = query_data["content"].replace(
                "##PORT##", str(net_orch.get_assigned_port(component))
            )
        case _:
            raise ValueError(
                f"Tipo de base de datos no soportado: {component.database_type}"
            )

    # Determinar la ruta completa del archivo de inicialización
    file_name = query_data["file_name"]
    file_full_path = os.path.join(path, file_name)

    # Abrir el archivo en modo escritura y escribir el contenido del query.
    # textwrap.dedent() elimina la indentación común de los strings multilinea,
    # asegurando que el contenido del archivo empiece sin espacios innecesarios.
    with open(file_full_path, "w") as f:
        f.write(textwrap.dedent(query_data["content"]))

    # --- Lógica específica post-escritura ---
    # Para el script de Elasticsearch, necesitamos hacerlo ejecutable después de escribirlo.
    if component.database_type == DatabaseType.ELASTICSEARCH:
        # Verificar que el archivo existe antes de cambiar sus permisos.
        # Aunque acabamos de escribirlo, esta verificación es una buena práctica.
        if os.path.exists(file_full_path):
            # 0o755 son los permisos octales para rwxr-xr-x (owner read/write/execute, group/others read/execute)
            os.chmod(file_full_path, 0o755)
