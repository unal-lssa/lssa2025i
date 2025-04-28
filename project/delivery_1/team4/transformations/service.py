from transformations.templates import generate_templated_component


def generate_service(component) -> None:
    """Generate a backend component with its endpoints"""

    # Prepare component data for templates
    component_data = {
        "name": component.name,
        "description": getattr(component, "description", None),
        "endpoints": [
            {
                "name": endpoint.name,
                "method": endpoint.method,
                "path": endpoint.path,
            }
            for endpoint in component.endpoints
        ],
    }

    generate_templated_component(
        name=component.name,
        template_name="service",
        params={"component": component_data},
    )
