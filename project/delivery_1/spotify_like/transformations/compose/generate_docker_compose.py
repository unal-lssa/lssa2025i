import os

def generate_docker_compose(architecture):
    # Genera el archivo docker-compose.yml basándose en el diccionario de arquitectura

    # Extraer los datos principales del diccionario de arquitectura
    components_data = architecture.get("components", {})
    connections_data = architecture.get("connections", {})
    replicas_data = architecture.get("replicas", {}) # Diccionario {nombre_servicio: numero_replicas}

    # Crear un mapa simple de nombre a tipo de componente para usar en el ordenamiento y bucles
    # Esto replica la estructura del argumento 'components' que tenía la función original.
    simple_components_map = {
        name: data.get("type") for name, data in components_data.items()
    }

    # Ruta donde se generará el archivo docker-compose.yml
    path = "skeleton/"
    os.makedirs(path, exist_ok=True) # Asegurarse de que la carpeta 'skeleton' exista

    with open(os.path.join(path, "docker-compose.yml"), "w") as f:
        # Ordenar componentes para generar primero las bases de datos, replicando la lógica original.
        sorted_components = dict(
            sorted(
                simple_components_map.items(),
                key=lambda item: 0 if item[1] in ["database", "db"] else 1,
            )
        )

        f.write("services:\n")

        port_counter = 8002 # Contador para asignar puertos incrementalmente

        # --- Primera pasada: Generar servicios de bases de datos ---
        # Iterar sobre los componentes ordenados. Si es una BD, generar su configuración.
        for name, comp_type in sorted_components.items():
             if comp_type in ["database", "db"]:
                 # Obtener detalles de la BD desde 'components_data'
                 db_details = components_data.get(name, {}).get("details", {})
                 # Obtener el tipo de BD, usando 'mysql' como valor por defecto si no se especifica
                 db_type = db_details.get("databaseType", "mysql").lower()

                 # Incrementar el contador de puertos y escribir la configuración específica de la BD.
                 # La lógica original incrementaba el puerto dentro de cada bloque de tipo de BD.
                 port_counter += 1

                 f.write(f"  {name}:\n")
                 if db_type == "mysql":
                     f.write("    image: mysql:8\n") # Imagen hardcodeada como en original
                     f.write("    environment:\n")
                     f.write("      - MYSQL_ROOT_PASSWORD=root\n") # Contraseña hardcodeada
                     f.write(f"      - MYSQL_DATABASE={name}\n") # Nombre de BD basado en el nombre del servicio
                     f.write("    volumes:\n")
                     f.write(f"      - ./{name}/init.sql:/docker-entrypoint-initdb.d/init.sql\n") # Volumen hardcodeado
                     f.write("    ports:\n")
                     f.write(f"      - '{port_counter}:3306'\n")

                 elif db_type == "postgresql":
                     f.write("    image: postgres:14\n") # Imagen hardcodeada
                     f.write("    environment:\n")
                     f.write("      - POSTGRES_PASSWORD=root\n") # Contraseña hardcodeada
                     f.write(f"      - POSTGRES_DB={name}\n") # Nombre de BD
                     f.write("    volumes:\n")
                     f.write(f"      - ./{name}/init.sql:/docker-entrypoint-initdb.d/init.sql\n") # Volumen hardcodeado
                     f.write("    ports:\n")
                     f.write(f"      - '{port_counter}:5432'\n")

                 elif db_type == "mongodb":
                     f.write("    image: mongo:6\n") # Imagen hardcodeada
                     f.write("    environment:\n")
                     f.write("      - MONGO_INITDB_ROOT_USERNAME=root\n") # Credenciales hardcodeadas
                     f.write("      - MONGO_INITDB_ROOT_PASSWORD=root\n")
                     f.write("    volumes:\n")
                     f.write(f"      - ./{name}/init-mongo.js:/docker-entrypoint-initdb.d/init-mongo.js:ro\n") # Volumen hardcodeado
                     f.write("    ports:\n")
                     f.write(f"      - '{port_counter}:27017'\n")

                 elif db_type == "elasticsearch":
                     f.write("    image: elasticsearch:7.17.0\n") # Imagen hardcodeada
                     f.write("    environment:\n")
                     f.write("      - discovery.type=single-node\n") # Config hardcodeada
                     f.write("      - bootstrap.memory_lock=true\n")
                     f.write('      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"\n')
                     f.write("    volumes:\n")
                     f.write(f"      - ./{name}/init-es.sh:/init-es.sh:ro\n") # Volumen hardcodeado
                     f.write('    command: ["/bin/sh", "-c", "elasticsearch & /init-es.sh"]\n') # Comando hardcodeado
                     f.write("    ports:\n")
                     f.write(f"      - '{port_counter}:9200'\n")

        # --- Segunda pasada: Generar otros servicios (backends, frontends, LBs, APIGW) ---
        # Iterar sobre todos los componentes (ordenados por consistencia con el original),
        # pero saltar los tipos que se manejan en otras pasadas.
        for name, comp_type in sorted_components.items():
            # Saltar tipos que se manejan en otras secciones (bases de datos, buckets, cdn, queue)
            if comp_type in ["database", "db", "bucket", "cdn", "queue"]:
                continue

            # Obtener detalles específicos de este componente
            comp_details = components_data.get(name, {}).get("details", {})
            # Obtener las conexiones de este componente
            component_connections = connections_data.get(name, {})
            # Obtener el número de réplicas (relevante para backends/frontends principalmente)
            # Usamos replicas_data del nuevo formato, con 1 como valor por defecto.
            replica_count = replicas_data.get(name, 1)

            # Determinar si este componente (backend/frontend) es objetivo de un LB para la lógica de puertos/instancias.
            # Esta bandera 'is_balanced' solo es relevante para backends/frontends en la lógica de instancias/puertos.
            is_balanced = False
            if comp_type in ["backend", "frontend"]:
                for lb_name, lb_data in components_data.items():
                     if lb_data.get("type") == "loadbalancer":
                         # Si el objetivo del LB coincide con el nombre del componente actual
                         if lb_data.get("details", {}).get("target") == name:
                             is_balanced = True
                             break


            # --- Lógica de generación por tipo de componente ---

            if comp_type == "loadbalancer":
                # Generar servicio para Load Balancer
                f.write(f"  {name}:\n")
                f.write(f"    build: ./{name}\n") # Se asume que la carpeta de build coincide con el nombre del componente

                # depends_on para LB: depende de TODAS las instancias del target
                # Esta sección de depends_on es específica de los LBs y no debe duplicarse con una general.
                lb_target_name = comp_details.get("target")
                if lb_target_name:
                    # Obtener el número de réplicas del servicio objetivo del LB.
                    target_replicas = replicas_data.get(lb_target_name, 1)
                    # Escribir la sección depends_on solo si hay al menos un target con >= 1 réplica.
                    if target_replicas > 0:
                        f.write("    depends_on:\n")
                        # Depender de cada instancia del servicio objetivo del LB.
                        # Replicamos el formato original 'target_name_i', que depende de cómo se nombran las instancias.
                        # Si el target tiene 1 réplica, esto escribirá '- target_name_0'.
                        for i in range(target_replicas):
                             f.write(f"      - {lb_target_name}_{i}\n")

                # Ports para LB: usar port_counter incremental y mapear a puerto 80 interno.
                # El puerto 80 interno es un supuesto común para frontends/LBs/APIGWs.
                port_counter += 1
                f.write("    ports:\n")
                f.write(f"      - '{port_counter}:80'\n")


            elif comp_type == "api_gateway":
                 # Generar servicio para API Gateway
                 f.write(f"  {name}:\n")
                 f.write(f"    build: ./{name}\n") # Build desde la carpeta del APIGW

                 # depends_on para APIGW: basado en sus conexiones salientes
                 # Esta es la lógica de depends_on para APIGWs, backends y frontends.
                 depends_on_list_from_connections = []
                 for outgoing_conn in component_connections.get("outgoing", []):
                      target_name = outgoing_conn.get("target")
                      if target_name and target_name != name: # Evitar dependencia de sí mismo
                          # Determinar el formato de la dependencia (nombre o nombre_0 si replicado)
                          target_replica_count = replicas_data.get(target_name, 1)
                          if target_replica_count > 1:
                              # Depender de la primera instancia si el objetivo está replicado (comportamiento original)
                              depends_on_list_from_connections.append(f"{target_name}_0")
                          else:
                              # Depender del nombre del servicio si no está replicado
                              depends_on_list_from_connections.append(target_name)

                 if depends_on_list_from_connections:
                      f.write("    depends_on:\n")
                      for dep in depends_on_list_from_connections:
                          f.write(f"      - {dep}\n")

                 # Ports para APIGW: usar port_counter incremental y mapear a puerto 80 interno.
                 port_counter += 1
                 f.write("    ports:\n")
                 f.write(f"      - '{port_counter}:80'\n")


            elif comp_type in ["backend", "frontend"]:
                # Generar servicios para Backends y Frontends
                # Estos pueden tener múltiples instancias o ser objetivos de LB (lo que afecta ports/instancias).
                # Usar replica_count y is_balanced para decidir si generar instancias replicadas o un servicio simple.
                # Usar depends_on_list_from_connections para depends_on.

                # Preparar depends_on basado en conexiones salientes para Backends/Frontends
                # Esta lógica es la misma que para API Gateways, ya que ambos dependen de sus targets salientes.
                depends_on_list_from_connections = []
                for outgoing_conn in component_connections.get("outgoing", []):
                     target_name = outgoing_conn.get("target")
                     if target_name and target_name != name: # Evitar dependencia de sí mismo
                         # Determinar el formato de la dependencia (nombre o nombre_0 si replicado)
                         target_replica_count = replicas_data.get(target_name, 1)
                         if target_replica_count > 1:
                             # Depender de la primera instancia si el objetivo está replicado (comportamiento original)
                             depends_on_list_from_connections.append(f"{target_name}_0")
                         else:
                             # Depender del nombre del servicio si no está replicado
                             depends_on_list_from_connections.append(target_name)

                if replica_count > 1 or is_balanced:
                    # Generar instancias replicadas (ej. backend_0, backend_1)
                    for i in range(replica_count):
                        instance_name = f"{name}_{i}"
                        f.write(f"  {instance_name}:\n")
                        f.write(f"    build: ./{name}\n") # Build desde la carpeta del componente base

                        # depends_on para instancias: basado en depends_on_list_from_connections
                        # Escribir depends_on si hay dependencias
                        if depends_on_list_from_connections:
                             f.write("    depends_on:\n")
                             for dep in depends_on_list_from_connections:
                                 f.write(f"      - {dep}\n")

                        # Ports: solo para la primera instancia (i == 0) Y si el servicio NO está balanceado.
                        # Esta es la lógica original de asignación de puertos para servicios con instancias.
                        if i == 0 and not is_balanced:
                            port_counter += 1 # Incrementar el puerto para cada nuevo mapeo de puerto
                            f.write("    ports:\n")
                            f.write(f"      - '{port_counter}:80'\n") 

                else: # Servicio simple (replica_count es 1 y no está balanceado)
                    # Generar una sola definición de servicio con el nombre original del componente.
                    f.write(f"  {name}:\n")
                    f.write(f"    build: ./{name}\n") # Build desde la carpeta del componente base

                    # depends_on para servicio simple: basado en depends_on_list_from_connections
                    # Escribir depends_on si hay dependencias
                    if depends_on_list_from_connections:
                         f.write("    depends_on:\n")
                         for dep in depends_on_list_from_connections:
                             f.write(f"      - {dep}\n")

                    # Ports: asignar un puerto si es una sola instancia y no está balanceado.
                    # Esta es la lógica original de asignación de puertos para servicios simples.
                    if comp_type in ["frontend"]:
                        f.write("    ports:\n")
                        f.write(f"      - '8001:80'\n") 
                    else:    
                        port_counter += 1 # Incrementar el puerto
                        f.write("    ports:\n")
                        f.write(f"      - '{port_counter}:80'\n") 

        # --- Cuarta pasada: Generar servicios de CDNs (Nginx) ---
        # Manejados en un bucle separado en el código original, mantenemos esta estructura.
        cdns = {name: comp_data for name, comp_data in components_data.items() if comp_data.get("type") == "cdn"}
        has_cdn = len(cdns) > 0 # Bandera para saber si incluir la sección de volumes al final

        # Los CDNs usan un puerto fijo (8080 -> 80), no se usa port_counter aquí.
        for name, comp_data in cdns.items():
             # Configuración específica de servicio Nginx para CDNs.
             f.write(f"  {name}:\n")
             f.write(f"    container_name: {name}\n") # Nombre del contenedor igual al nombre del servicio
             f.write(f"    build:\n")
             f.write(f"      context: ./{name}\n") # La carpeta de build es la del CDN
             f.write(f"    ports:\n")
             f.write(f"      - '8080:80'\n") # Mapeo de puerto hardcodeado como en original
             f.write("    volumes:\n")
             # Montaje del archivo de configuración de Nginx y volumen de cache.
             # Los nombres de volumen y ruta están hardcodeados a 'songs_cdn' como en original.
             f.write(f"      - ./songs_cdn/nginx.conf:/etc/nginx/nginx.conf:ro\n")
             f.write(f"      - nginx_cache:/tmp/nginx_cache\n") # Nombre de volumen 'nginx_cache', replicado
             # No se especifica 'depends_on' para CDNs en el original.

        # --- Quinta pasada: Generar servicios de Colas (Kafka) y Zookeeper ---
        # Manejados en un bloque separado en el código original, mantenemos esta estructura.
        queues = {name: comp_data for name, comp_data in components_data.items() if comp_data.get("type") == "queue"}
        if len(queues) > 0:
             # Si hay colas, necesitamos Zookeeper.
             f.write("\n  zookeeper:\n")
             f.write("    image: confluentinc/cp-zookeeper:7.9.0\n") # Imagen hardcodeada
             f.write("    container_name: zookeeper\n") # Nombre del contenedor hardcodeado
             f.write("    environment:\n")
             f.write("      ZOOKEEPER_CLIENT_PORT: 2181\n") # Variables de entorno hardcodeadas
             f.write("      ZOOKEEPER_TICK_TIME: 2000\n")
             f.write("    ports:\n")
             f.write("      - '2181:2181'\n") # Mapeo de puerto hardcodeado

             queue_id = 1 # Contador para el ID del broker Kafka y el mapeo de puertos
             # Las colas usan un puerto base (9092) + offset, no se usa port_counter aquí.
             for name, comp_data in queues.items():
                 # Configuración específica de servicio Kafka.
                 f.write(f"  {name}:\n")
                 f.write(f"    image: confluentinc/cp-kafka:latest\n") # Imagen latest hardcodeada
                 f.write(f"    container_name: {name}\n") # Nombre del contenedor igual al servicio
                 f.write("    environment:\n")
                 f.write(f"      KAFKA_BROKER_ID: {queue_id}\n") # ID incremental del broker
                 f.write(f"      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181\n") # Dependencia de Zookeeper en env
                 f.write(f"      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://{name}:9092\n") # Listener publicitado usando el nombre del servicio
                 f.write(f"      KAFKA_LISTENERS: PLAINTEXT://0.0.0.0:9092\n") # Listener interno
                 f.write("      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1\n") # Config hardcodeada
                 f.write("      KAFKA_AUTO_CREATE_TOPICS_ENABLE: 'true'\n") # Config hardcodeada
                 f.write("    ports:\n")
                 # Mapeo de puerto incremental basado en el ID de la cola.
                 f.write(f"      - '{9092 + (queue_id - 1)}:{9092 + (queue_id - 1)}'\n")
                 f.write("    depends_on:\n")
                 f.write("      - zookeeper\n") # Dependencia explícita de Zookeeper en depends_on
                 queue_id += 1 # Incrementar para la próxima cola

        # --- Sexta pasada: Generar servicios del bucket ---
        buckets = {name: comp_data for name, comp_data in components_data.items() if comp_data.get("type") == "bucket"}
        # Inicializar un contador de puertos específico para buckets
        bucket_port_counter = 4566
        if len(buckets) > 0:
            for name, comp_data in buckets.items():
                f.write(f"  {name}:\n")
                f.write(f"    container_name: ${{LOCALSTACK_DOCKER_NAME:-{name}}}\n")
                f.write(f"    build:\n")
                f.write(f"      context: ./{name}\n")
                f.write(f"    ports:\n")
                f.write(f"      - '{bucket_port_counter}:4566'\n")
                f.write(f"    environment:\n")
                f.write(f"      - DEBUG=${{DEBUG:-0}}\n")
                f.write(f"    volumes:\n")
                f.write(f"      - ${{LOCALSTACK_VOLUME_DIR:-./volume}}:/var/lib/localstack\n")
                f.write(f"      - /var/run/docker.sock:/var/run/docker.sock\n")
                bucket_port_counter += 1

        # --- Sección de Volumes (debe estar al final del archivo docker-compose) ---
        if has_cdn:
             f.write("\nvolumes:\n")
             # Definición del volumen de cache de Nginx, nombre hardcodeado, replicado.
             f.write("  nginx_cache:\n")