from pathlib import Path

PROJECT_BASE = Path.cwd() / "skeleton"
TEMPLATES_BASE = Path(__file__).parent / "templates"


def _make_component_dir(component_name: str, project_base: Path = PROJECT_BASE) -> Path:
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

    for template in template_path.iterdir():
        with template.open("r") as template_file:
            content = template_file.read()

        if params is not None:
            for param, value in params.items():
                content = content.replace(f"{{{{{param}}}}}", value)

        with (target_path / template.name).open("w") as target_file:
            target_file.write(content)


def generate_templated_component(
    name: str, template_name: str, params: dict = None
) -> None:
    """Generate a templated component

    A templated component is that for which the only logic in generating is
    copying the files of a template and replacing some params in the templates.
    """

    path = _make_component_dir(name)

    _copy_template(
        template_path=TEMPLATES_BASE / template_name, target_path=path, params=params
    )


def generate_database(name):
    generate_templated_component(name, "database")


def generate_backend(name, database):
    generate_templated_component(
        name,
        "backend",
        params={
            "database": database,
        },
    )


def generate_frontend(name, backend):
    generate_templated_component(
        name,
        "frontend",
        params={
            "backend": backend,
        },
    )


def generate_docker_compose(components):
    path = _make_component_dir("")

    with (path / "docker-compose.yml").open("w") as f:
        sorted_components = dict(
            sorted(
                components.items(), key=lambda item: 0 if item[1] == "database" else 1
            )
        )

        f.write("services:\n")

        db = None

        for i, (name, ctype) in enumerate(sorted_components.items()):
            port = 8000 + i
            f.write(f"\n  {name}:\n")

            if ctype == "database":
                db = name
                f.write("    image: mysql:8\n")
                f.write("    environment:\n")
                f.write("      - MYSQL_ROOT_PASSWORD=root\n")
                f.write(f"      - MYSQL_DATABASE={name}\n")
                f.write("    volumes:\n")
                f.write(
                    f"        - ./{name}/init.sql:/docker-entrypoint-initdb.d/init.sql\n"
                )
                f.write("    ports:\n")
                f.write("      - '3306:3306'\n")

            elif ctype == "load_balancer":
                pass

            else:
                f.write(f"    build: ./{name}\n")
                f.write(f"    ports:\n      - '{port}:80'\n")

                if ctype == "backend":
                    f.write(f"    depends_on:\n      - {db}\n")

        f.write("\nnetworks:\n  default:\n    driver: bridge\n")


def apply_transformations(model):
    components = {}
    backend_name = None
    database_name = None

    for e in model.elements:
        if e.__class__.__name__ == "Component":
            if e.type == "backend":
                backend_name = e.name
            elif e.type == "database":
                database_name = e.name

    for e in model.elements:
        if e.__class__.__name__ == "Component":
            components[e.name] = e.type
            if e.type == "database":
                generate_database(e.name)
            elif e.type == "backend":
                generate_backend(e.name, database=database_name)
            elif e.type == "frontend":
                generate_frontend(e.name, backend=backend_name)

    generate_docker_compose(components)
