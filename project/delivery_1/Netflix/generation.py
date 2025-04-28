from metamodel import create_metamodel
from transformations import apply_transformations
from generators import generate_docker_compose


def model_to_dict(model):
    architecture = {
        "frontend": [],
        "services": [],
        "databases": [],
        "storages": [],
        "caches": [],
        "event_streams": [],
        "connectors": [],
        "loadbalancers": []
    }

    for elem in model.elements:
        elem_type = elem.__class__.__name__.lower()
        
        elem_details = {"name": elem.name, "category": elem.type}

        # Cargar propiedades generales
        if hasattr(elem, "properties"):
            for prop in elem.properties:
                elem_details[prop.name] = prop.value.strip('"')

        # Propiedades especiales
        if hasattr(elem, "port"):
            elem_details["port"] = elem.port
        if hasattr(elem, "timeout"):
            elem_details["timeout"] = elem.timeout
        if hasattr(elem, "connection_pool"):
            elem_details["connection_pool"] = elem.connection_pool
        if hasattr(elem, "ttl"):
            elem_details["ttl"] = elem.ttl
        if hasattr(elem, "topic"):
            elem_details["topic"] = elem.topic
        if hasattr(elem, "encryption"):
            elem_details["encryption"] = elem.encryption

        # Clasificación
        if elem_type == "component":
            if elem.type in ["frontend", "mobile_client"]:
                architecture["frontend"].append(elem_details)
            else:
                architecture["services"].append(elem_details)
        elif elem_type == "database":
            if elem.type == "storage":
                architecture["storages"].append(elem_details)
            else:
                architecture["databases"].append(elem_details)
        elif elem_type == "cache":
            architecture["caches"].append(elem_details)
        elif elem_type == "eventstream":
            architecture["event_streams"].append(elem_details)
        elif elem_type == "loadbalancers":
            architecture["loadbalancers"].append(elem_details)
       
        else:
            print(f"Elemento no manejado: {elem_type}")

    return architecture

    
if __name__ == '__main__':
    
    metamodel = create_metamodel()
    model = metamodel.model_from_file('model.arch')
    architecture = model_to_dict(model)
    print("archi",architecture)
    apply_transformations(architecture)
    # generate_docker_compose(architecture)