import os

from textx import metamodel_from_file

def create_metamodel():
    grammar_path = os.path.join(os.path.dirname(__file__), 'arch.tx')
    return metamodel_from_file(grammar_path)