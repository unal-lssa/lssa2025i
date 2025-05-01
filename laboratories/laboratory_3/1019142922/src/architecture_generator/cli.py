"""Entrypoint for generation app"""

from pathlib import Path
import typer

from architecture_generator import transformations
from architecture_generator.metamodel import create_metamodel

app = typer.Typer()


@app.command()
def main(
    model_file: Path,
    output_dir: Path = Path("skeleton"),
):
    metamodel = create_metamodel()
    model = metamodel.model_from_file(model_file)
    transformations.apply(model, output_dir)
