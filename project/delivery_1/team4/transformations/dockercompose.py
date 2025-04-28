from transformations.templates import generate_templated_component 


def generate_docker_compose(model):
    """Generate the docker compose for the system"""

    params = {
        "name": getattr(model, "name", "System Architecture"),
        "components": [
            {
                "name": component.name,
            }
            for component in model.elements
            if component.__class__.__name__ == "Component"
        ],
    }

    generate_templated_component(name="", template_name="docker-compose", params=params)
