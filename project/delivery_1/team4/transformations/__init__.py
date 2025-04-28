from transformations import database, gateway, frontend, service, broker


def apply_transformations(model):
    components = {}

    connectors = []
    for e in model.elements:
        if e.__class__.__name__ == "Connector":
            connectors.append(
                {"from": e.from_.name, "to": e.to_.name, "type": e.to_.type}
            )

    for e in model.elements:
        if e.__class__.__name__ == "Component":
            components[e.name] = e
            # if e.type == "database":
            #     database.generate_database(e.name)
            """ if e.type == "gateway":
                gateway.generate_gateway(e.name, model)
            if e.type == "service":
                service.generate_service(e) """
            if e.type == "frontend":
                api_gateway = next(
                    (
                        connector["to"]
                        for connector in connectors
                        if (
                            connector["from"] == e.name
                            and connector["type"] == "gateway"
                        )
                    ),
                    None,
                )
                real_time_service = next(
                    (
                        connector["to"]
                        for connector in connectors
                        if (
                            connector["from"] == e.name
                            and connector["type"] == "service"
                        )
                    ),
                    None,
                )
                frontend.generate_frontend(e.name, api_gateway, real_time_service)
            if e.type == "broker":
                broker.generate_broker(e.name)
    # generate_docker_compose(components)
