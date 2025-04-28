from pathlib import Path

import jinja2

PROJECT_BASE = Path.cwd() / "skeleton"
TEMPLATES_BASE = Path.cwd() / "templates"


def _make_dir(dir_name: str, dir_path: Path) -> Path:
    """Create the location for a given component"""

    path = dir_path / dir_name
    path.mkdir(parents=True, exist_ok=True)
    return path


def _copy_template(
    template_path: Path, target_path: Path, params: dict | None = None
) -> None:
    """
    Make a copy of the files in a template directory to the target location and replace
    the parameters in templates.
    """

    jinja_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(template_path),
    )

    for item in template_path.iterdir():
        # If the item is a directory, create the corresponding directory in the target path
        if item.is_dir():
            new_target = _make_dir(item.name, target_path)
            # Recursively copy the contents of the directory
            _copy_template(item, new_target, params)

        elif item.is_file():
            # If the item is a file, process it as a template
            template = jinja_env.get_template(item.name)
            target_file_path = target_path / item.stem
            with target_file_path.open("w") as target_file:
                target_file.write(template.render(**params))

def generate_templated_component(
    name: str,
    template_name: str,
    params: dict | None = None,
) -> None:
    """Generate a templated component
    A templated component is that for which the only logic in generating is
    copying the files of a template and replacing some params in the templates.
    """
    if params is None:
        params = {}


    path = _make_dir(name, PROJECT_BASE)
    _copy_template(
        template_path=TEMPLATES_BASE / template_name, target_path=path, params=params
    )
