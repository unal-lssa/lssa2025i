from .database.generate_database import generate_database
from .backend.generate_backend import generate_backend
from .frontend.generate_frontend import generate_frontend
from .load_balancer.generate_load_balancer import generate_loadbalancer
from .compose.generate_docker_compose import generate_docker_compose
from .api_gateway.generate_api_gateway import generate_api_gateway
def process_connectors(model):
    """Process all connectors in the model and return a mapping of component connections."""
    component_connections = {}
    
    for e in model.elements:
        if e.__class__.__name__ == 'Connector':
            source_component = getattr(e, 'from').name
            conn_type = e.type
            targets = e.to if isinstance(e.to, list) else [e.to]  # Always work with a list

            if source_component not in component_connections:
                component_connections[source_component] = {}

            if conn_type not in component_connections[source_component]:
                component_connections[source_component][conn_type] = []

            for target in targets:
                component_connections[source_component][conn_type].append(target.name)
    
    print(f"Component connections: {component_connections}")
    return component_connections

def apply_transformations(model):
    components = {}
    replicas = {}
    load_balancer_config = {}
    database_name = None
    db_types = {}
    api_gateway_name = None
    
    # Process components first
    for e in model.elements:
        if e.__class__.__name__ == 'Component' or e.__class__.__name__ == 'StandardComponent':
            components[e.name] = e.type
            
            if e.type == 'database' or e.type == 'db':
                database_name = e.name
                if hasattr(e, 'databaseType'):
                    db_types[e.name] = e.databaseType
                
            if hasattr(e, 'instances') and e.instances is not None:
                replicas[e.name] = e.instances.count
        
        elif e.__class__.__name__ == 'Database':
            components[e.name] = 'db'
            database_name = e.name
            if hasattr(e, 'databaseType'):
                db_types[e.name] = e.databaseType
        
        elif e.__class__.__name__ == 'LoadBalancer':
            load_balancer_name = e.name
            components[load_balancer_name] = 'loadbalancer'
            
            if hasattr(e, 'target') and e.target is not None:
                target_name = e.target.name
                load_balancer_config[load_balancer_name] = target_name
                
                if target_name not in replicas and hasattr(e, 'instanceCount'):
                    replicas[target_name] = e.instanceCount

        elif e.__class__.__name__ == 'ApiGateway':
            api_gateway_name = e.name
            components[api_gateway_name] = 'api_gateway'
    
    # Process connectors
    component_connections = process_connectors(model)
    
    # Generate components with their connections
    for e in model.elements:
        if e.__class__.__name__ == 'Component' or e.__class__.__name__ == 'StandardComponent':
            if e.type == 'database' or e.type == 'db':
                generate_database(e.name, db_types.get(e.name, 'mysql'))
            elif e.type == 'backend':
                connections = component_connections.get(e.name, {})
                
                # Determine database type based on connection
                backend_db_type = 'mysql'  # default
                if connections and 'db_connector' in connections:
                    connected_db = connections['db_connector']
                    for db in connected_db:
                        if db in db_types:
                            backend_db_type = db_types[db]
                            break
                generate_backend(e.name, database=database_name, database_type=backend_db_type, connections=connections)
            elif e.type == 'frontend':
                # Connect frontend to load balancer if it exists, otherwise connect to backend
                backend_service = None
                target_name = None
                for lb_name, target_name in load_balancer_config.items():
                    backend_service = lb_name
                    break
                
                connections = component_connections.get(e.name, {})
                generate_frontend(e.name, backend=backend_service if backend_service else target_name,
                                 connections=connections)
        
        elif e.__class__.__name__ == 'Database':
            generate_database(e.name, e.databaseType if hasattr(e, 'databaseType') else 'mysql')
            
        elif e.__class__.__name__ == 'LoadBalancer':
            target_name = load_balancer_config.get(e.name)
            if target_name:
                replica_count = replicas.get(target_name, 1)
                generate_loadbalancer(e.name, target_name, replica_count)
        elif e.__class__.__name__ == 'ApiGateway':
            connections = component_connections.get(e.name, {})  
            route_map = {}

            http_targets = connections.get('http', [])

            for target in http_targets:
                route_map[target] = target 
                
            generate_api_gateway(e.name, route_map)

    generate_docker_compose(components, replicas, load_balancer_config, db_types)