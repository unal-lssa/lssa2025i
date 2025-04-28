from pathlib import Path
import jinja2

from .templates import PROJECT_BASE, TEMPLATES_BASE


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

def generate_service(component, target_path: Path = PROJECT_BASE) -> None:
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
        ]
    }

    generate_templated_component(
        name=component.name,
        template_name="service",
        target_path=target_path,
        params={"component": component_data}
    )
