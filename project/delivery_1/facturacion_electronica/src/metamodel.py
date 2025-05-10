import os

from textx import metamodel_from_file

def create_metamodel():
    return metamodel_from_file(os.path.join(os.path.dirname(__file__), "arch.tx"))
