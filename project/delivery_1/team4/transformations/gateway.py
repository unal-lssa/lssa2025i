from transformations.templates import generate_templated_component


def generate_gateway(name, model):
    services = {}

    for e in model.elements:
        if e.__class__.__name__ == "Connector":
            if e.from_.name == name:
                services[e.to_.name] = e.to_

    routes = ""
    for s in services:
        service = services[s]
        routes += f"""\n  /{service.name}:\n    backend: "http://{service.name}:5000"\n"""

    generate_templated_component(
        name,
        "api-gateway",
        params={
            "routes": routes,
        },
    )

def generate_gateway_dockercompose(name, model):
    services = {}

    for e in model.elements:
        if e.__class__.__name__ == "Connector":
            if e.from_.name == name:
                services[e.to_.name] = e.to_

    docker_compose_service = f"""\n  {name}:\n    build: ./{name}\n    ports:\n      - "5000:5000"\n    restart: unless-stopped\n"""

    if len(services) > 0:
        docker_compose_service += "    depends_on:\n"

    for s in services:
        docker_compose_service += f"""      - {s}\n"""

    print(docker_compose_service)

    return docker_compose_service
