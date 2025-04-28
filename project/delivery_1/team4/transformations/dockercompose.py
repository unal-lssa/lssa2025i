import dataclasses
from collections import defaultdict

from transformations.templates import generate_templated_component


@dataclasses.dataclass
class ComponentConfig:
    name: str = None
    public: bool = False
    networks: set[str] = dataclasses.field(default_factory=set)


def generate_docker_compose(model):
    """Generate the docker compose for the system"""

    components = defaultdict(ComponentConfig)

    for element in model.elements:
        match element.__class__.__name__:
            case "Component":
                component_config = components[element.name]
                component_config.name = element.name
                component_config.port = element.port
                if element.visibility == "public":
                    component_config.public = element.visibility == "public"
                    component_config.networks.add("public")
                if element.visibility == "internal":
                    component_config.networks.add("internal")

            case "Connector":
                from_component = components[element.from_.name]

                from_component.networks.add(element.to_.visibility)

    params = {
        "name": getattr(model, "name", "System Architecture"),
        "components": components.values(),
    }

    generate_templated_component(name="", template_name="docker-compose", params=params)
