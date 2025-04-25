from transformations import database, gateway

def apply_transformations(model):
    components = {}

    # print(model.elements)

    for e in model.elements:
        if e.__class__.__name__ == "Component":
            components[e.name] = e
            # if e.type == "database":
            #     database.generate_database(e.name)
            if e.type == "gateway":
                gateway.generate_gateway(e.name, model)
            # if e.type == "service":
            #     generate_database(e.name)
            # if e.type == "frontend":
            #     generate_database(e.name)

    # generate_docker_compose(components)
