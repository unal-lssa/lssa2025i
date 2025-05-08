import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), "../..", "src"))

from Generation.metamodel import create_metamodel
from Generation.transformations import generate_architecture

if __name__ == "__main__":
    metamodel = create_metamodel()
    model = metamodel.model_from_file("model.arch")
    generate_architecture(model)
