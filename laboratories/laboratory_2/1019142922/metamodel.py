import os

from textx import metamodel_from_file


def component_processor(component):
    """Object processor to handle default values of components"""

    if component.replicas == 0:
        component.replicas = 1


def create_metamodel():
    grammar = os.path.join(os.path.dirname(__file__), "arch.tx")

    metamodel = metamodel_from_file(grammar)

    metamodel.register_obj_processors(
        {
            "Component": component_processor,
        }
    )

    return metamodel
