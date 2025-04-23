import os

from metamodel import create_metamodel
from transformations import apply_transformations

if __name__ == "__main__":

    metamodel = create_metamodel()
    model = metamodel.model_from_file(os.path.join(os.path.dirname(__file__), "model.arch"))
    apply_transformations(model)
