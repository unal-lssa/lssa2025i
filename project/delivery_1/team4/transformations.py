from pathlib import Path

PROJECT_BASE = Path.cwd() / "skeleton"
TEMPLATES_BASE = Path(__file__).parent / "templates"

#Create the location for a given component
def _make_component_dir(component_name: str, project_base: Path = PROJECT_BASE) -> Path:
    path = project_base / component_name
    path.mkdir(parents=True, exist_ok=True)
    return path

# Make a copy of the files in a template directory to the target location and replace
# the parameters in templates.
def _copy_template(template_path: Path, target_path: Path, params: dict | None = None) -> None:
    for template in template_path.iterdir():
        with template.open("r") as template_file:
            content = template_file.read()

        if params is not None:
            for param, value in params.items():
                content = content.replace(f"{{{{{param}}}}}", value)

        with (target_path / template.name).open("w") as target_file:
            target_file.write(content)


# A templated component is that for which the only logic in generating is
# copying the files of a template and replacing some params in the templates.
def generate_templated_component(name: str, template_name: str, params: dict = None) -> None:
    path = _make_component_dir(name)
    _copy_template(template_path=TEMPLATES_BASE / template_name, target_path=path, params=params)


def generate_database(name):
    generate_templated_component(name, "database")


def generate_docker_compose(components):
    path = _make_component_dir("")

def apply_transformations(model):
    components = {}

    for e in model.elements:
        if e.__class__.__name__ == "Component":
            components[e.name] = e
            if e.type == "database":
                generate_database(e.name)

    # generate_docker_compose(components)
