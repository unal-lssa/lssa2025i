import os, textwrap

# --- Definición de las estructuras de Queries separadas ---

# Estructura de Query para MySQL
MYSQL_INIT_QUERY = {
    'file_name': 'init.sql',
    'content': """
            -- MySQL init query
            CREATE TABLE IF NOT EXISTS systems (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255)
            );
        """
}

# Estructura de Query por defecto para PostgreSQL
POSTGRESQL_DEFAULT_INIT_QUERY = {
    'file_name': 'init.sql',
    'content': """
            -- Default PostgreSQL init query
            CREATE TABLE IF NOT EXISTS generic_data (
                id SERIAL PRIMARY KEY,
                value VARCHAR(255)
            );
        """
}

# Estructura de Query específica para PostgreSQL de autenticación
POSTGRESQL_AUTH_INIT_QUERY = {
    'file_name': 'init.sql', 
    'content': """
            -- PostgreSQL auth init query: Base de datos para autenticación
            CREATE TABLE users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL
            );
            -- Índice para búsquedas rápidas por nombre de usuario
            CREATE INDEX idx_users_username ON users (username);
            -- Puedes añadir otras tablas necesarias para autenticación si aplica (ej. roles, permisos)
        """
}

# Estructura de Query para MongoDB
MONGODB_INIT_QUERY = {
    'file_name': 'init-mongo.js',
    'content': """
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
        """
}

# Estructura de Query para Elasticsearch
ELASTICSEARCH_INIT_QUERY = {
    'file_name': 'init-es.sh',
    'content': """
            #!/bin/bash
            # Esperar a que Elasticsearch esté listo (tiempo de espera heurístico)
            sleep 40
            # Crear un índice 'systems' con un mapeo básico.
            # Usar 127.0.0.1 en lugar de localhost para mejor compatibilidad en entornos Docker
            curl -X PUT "127.0.0.1:9200/systems?pretty" -H 'Content-Type: application/json' -d '
            {
                "mappings": {
                   "properties": {
                       "name": { "type": "text" }
                   }
                }
            }
            '
            # Puedes añadir comandos adicionales para crear otros índices o pipelines aquí
        """
}

# Diccionario para mapear tipos de BD a sus queries por defecto
# Esto simplifica la búsqueda para la mayoría de los casos.
DEFAULT_QUERIES = {
    'mysql': MYSQL_INIT_QUERY,
    'postgresql': POSTGRESQL_DEFAULT_INIT_QUERY,
    'mongodb': MONGODB_INIT_QUERY,
    'elasticsearch': ELASTICSEARCH_INIT_QUERY,
}

# --- Declaración de la función generate_database modificada ---

def generate_database(name, db_type='mysql'):
    # Construir la ruta de salida específica para esta base de datos
    path = f'skeleton/{name}'
    # Crear el directorio si no existe (similar a os.makedirs(..., exist_ok=True))
    if not os.path.exists(path):
        os.makedirs(path)

    # Variable para almacenar la estructura del query que vamos a usar
    query_data = None
    # Convertir el tipo de BD a minúsculas para una comparación consistente
    db_type_lower = db_type.lower()

    # --- Lógica para seleccionar el query correcto ---
    # Primero, verificar si es el caso especial de PostgreSQL para autenticación
    if db_type_lower == 'postgresql' and "auth" in name.lower():
        # Si es PostgreSQL y el nombre de la BD contiene "auth", usar el script de autenticación.
        query_data = POSTGRESQL_AUTH_INIT_QUERY
    else:
        # Para todos los demás tipos de BD (MySQL, MongoDB, Elasticsearch)
        # y para PostgreSQL que no sea de autenticación, buscar el query
        # por defecto en el diccionario DEFAULT_QUERIES.
        query_data = DEFAULT_QUERIES.get(db_type_lower)

    # --- Verificación y escritura del archivo de query ---
    # Si query_data es None, significa que el 'db_type' proporcionado no se encontró
    # en nuestra lógica o en los queries por defecto.
    if query_data is None:
        # Preparar un mensaje de error útil listando los tipos soportados.
        # Incluimos los tipos presentes en DEFAULT_QUERIES.
        supported_types = list(DEFAULT_QUERIES.keys())
        # Podríamos añadir una nota sobre el caso especial de PostgreSQL si queremos ser más explícitos.
        # Ejemplo: supported_types.append("postgresql (para bases de datos con 'auth' en el nombre)")
        raise ValueError(
            f"Tipo de base de datos no soportado o query específico no encontrado para '{name}' ({db_type}). "
            f"Tipos soportados (y casos especiales manejados): {', '.join(supported_types)}"
        )

    # Determinar la ruta completa del archivo de inicialización
    file_name = query_data['file_name']
    file_full_path = os.path.join(path, file_name)

    # Abrir el archivo en modo escritura y escribir el contenido del query.
    # textwrap.dedent() elimina la indentación común de los strings multilinea,
    # asegurando que el contenido del archivo empiece sin espacios innecesarios.
    with open(file_full_path, 'w') as f:
        f.write(textwrap.dedent(query_data['content']))

    # --- Lógica específica post-escritura ---
    # Para el script de Elasticsearch, necesitamos hacerlo ejecutable después de escribirlo.
    if db_type_lower == 'elasticsearch':
        # Verificar que el archivo existe antes de cambiar sus permisos.
        # Aunque acabamos de escribirlo, esta verificación es una buena práctica.
        if os.path.exists(file_full_path):
            # 0o755 son los permisos octales para rwxr-xr-x (owner read/write/execute, group/others read/execute)
            os.chmod(file_full_path, 0o755)