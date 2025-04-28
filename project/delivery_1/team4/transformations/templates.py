from pathlib import Path

PROJECT_BASE = Path.cwd() / "skeleton"
TEMPLATES_BASE = Path.cwd() / "templates"


# Create the location for a given component
def _make_component_dir(component_name: str, project_base: Path = PROJECT_BASE) -> Path:
    path = project_base / component_name
    path.mkdir(parents=True, exist_ok=True)
    return path


# Make a copy of the files in a template directory to the target location and replace
# the parameters in templates.

def _copy_template(
    template_path: Path, target_path: Path, params: dict | None = None
) -> None:
    for template in template_path.rglob("*"):
        if template.is_file():

            relative_path = template.relative_to(template_path)
            target_file = target_path / relative_path

            target_file.parent.mkdir(parents=True, exist_ok=True)

            with template.open("r") as template_file:
                content = template_file.read()

            if params is not None:
                for param, value in params.items():
                    content = content.replace(f"{{{{{param}}}}}", value)

            with (target_file).open("w") as target_file:
                target_file.write(content)


# A templated component is that for which the only logic in generating is
# copying the files of a template and replacing some params in the templates.
def generate_templated_component(
    name: str, template_name: str, params: dict = None
) -> None:
    path = _make_component_dir(name)
    _copy_template(
        template_path=TEMPLATES_BASE / template_name, target_path=path, params=params
    )
