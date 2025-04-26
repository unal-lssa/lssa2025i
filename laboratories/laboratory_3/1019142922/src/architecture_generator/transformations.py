from pathlib import Path
import json
import jinja2
import logging

logger = logging.getLogger(__name__)

TEMPLATES_BASE = Path(__file__).parent / "templates"


def _make_component_dir(component_name: str, project_base: Path) -> Path:
    """Create the location for a given component"""

    path = project_base / component_name
    path.mkdir(parents=True, exist_ok=True)

    return path


def _copy_template(
    template_path: Path, target_path: Path, params: dict | None = None
) -> None:
    """
    Make a copy of the files in a template directory to the target location and replace
    the parameters in templates.
    """
    if params is None:
        params = {}

    jinja_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(template_path),
    )

    for template_file in template_path.iterdir():
        template = jinja_env.get_template(template_file.name)

        with (target_path / template_file.stem).open("w") as target_file:
            target_file.write(template.render(**params))


def generate_templated_component(
    name: str,
    template_name: str,
    target_path: Path,
    params: dict | None = None,
) -> None:
    """Generate a templated component

    A templated component is that for which the only logic in generating is
    copying the files of a template and replacing some params in the templates.
    """
    if params is None:
        params = {}

    path = _make_component_dir(name, target_path)
    _copy_template(template_path=TEMPLATES_BASE / template_name, target_path=path, params=params)


def generate_docker_compose(components, target_dir):
    """Generate docker-compose.yml using template"""
    path = _make_component_dir("", target_dir)
    
    # Sort components to ensure database is first
    sorted_components = dict(
        sorted(
            components.items(),
            key=lambda item: 0 if item[1].type == "database" else 1,
        )
    )
    
    # Find the database component
    db_component = next(
        (name for name, component in sorted_components.items() 
         if component.type == "database"),
        None
    )
    
    # Prepare template data
    template_data = {
        "components": sorted_components,
        "db_component": db_component
    }
    
    # Use the template engine to generate docker-compose.yml
    _copy_template(
        template_path=TEMPLATES_BASE / "docker-compose",
        target_path=path,
        params=template_data
    )


def generate_frontend_component(component, target_path: Path) -> None:
    """Generate a frontend component with its static files"""
    # Prepare component data for templates
    component_data = {
        "name": component.name,
        "description": getattr(component, "description", "Web Application")
    }
    
    generate_templated_component(
        name=component.name,
        template_name="frontend",
        target_path=target_path,
        params={"component": component_data}
    )


def generate_database_component(component, target_path: Path) -> None:
    """Generate a database component with initialization script"""
    # Prepare component data for templates
    component_data = {
        "name": component.name,
        "description": getattr(component, "description", "Database Service")
    }
    
    generate_templated_component(
        name=component.name,
        template_name="database",
        target_path=target_path,
        params={"component": component_data}
    )


def generate_backend_component(component, target_path: Path) -> None:
    """Generate a backend component with its endpoints"""
    # Prepare component data for templates
    component_data = {
        "name": component.name,
        "description": getattr(component, "description", "API Service"),
        "endpoints": [
            {
                "name": endpoint.name,
                "method": endpoint.method,
                "path": endpoint.path,
                "auth_methods": endpoint.auth_methods if hasattr(endpoint, 'auth_methods') else []
            }
            for endpoint in component.endpoints
        ]
    }
    
    generate_templated_component(
        name=component.name,
        template_name="backend",
        target_path=target_path,
        params={"component": component_data}
    )


def generate_api_gateway_config(components, target_path: Path) -> None:
    """Generate API gateway configuration that collects all exposed endpoints"""
    gateway_config = {
        "routes": []
    }
    
    for component in components.values():
        if component.type == "backend" and hasattr(component, 'exposes'):
            for exposed in component.exposes:
                route = {
                    "path": exposed.public_path if hasattr(exposed, 'public_path') else exposed.endpoint.path,
                    "target": f"http://{component.name}:8000{exposed.endpoint.path}",
                    "method": exposed.endpoint.method,
                    "auth_methods": exposed.endpoint.auth_methods if hasattr(exposed.endpoint, 'auth_methods') else []
                }
                gateway_config["routes"].append(route)
    
    # Write API gateway config
    with (target_path / "api_gateway.json").open("w") as f:
        json.dump(gateway_config, f, indent=2)


def generate_api_gateway(components, target_path: Path) -> None:
    """Generate the API gateway component"""

    # Create the api_gateway directory
    path = _make_component_dir("api_gateway", target_path)

    # First generate the configuration
    generate_api_gateway_config(components, path)
    
    # Then generate the API gateway application
    generate_templated_component(
        name="api_gateway",
        template_name="api_gateway",
        target_path=target_path,
        params={}
    )


transformations = {
    "database": generate_database_component,
    "backend": generate_backend_component,
    "frontend": generate_frontend_component,
}

def apply(model, output_dir):
    components = {}
    output_path = Path(output_dir)
    
    # First pass: collect all components
    for e in model.elements:
        if e.__class__.__name__ == "Component":
            components[e.name] = e
    
    # Second pass: generate components
    for component in components.values():
        try:
            transformations[component.type](component, output_path)
        except KeyError:
            logger.warning(f"Skipping component {component.name} of type {component.type}")
    
    # Generate API gateway
    generate_api_gateway(components, output_path)
    
    # Generate docker-compose
    generate_docker_compose(components, output_path)
