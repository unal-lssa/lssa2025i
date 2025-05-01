from pathlib import Path

from textx import metamodel_from_file


def create_metamodel():
    grammar_file = Path(__file__).parent / "arch.tx"

    metamodel = metamodel_from_file(grammar_file)

    return metamodel
