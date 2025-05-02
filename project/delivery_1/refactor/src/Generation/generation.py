from .metamodel import create_metamodel
from .transformations import extract_architecture_data, generate_architecture

if __name__ == "__main__":
    metamodel = create_metamodel()
    model = metamodel.model_from_file("model.arch")
    architecture_data = extract_architecture_data(model)
    generate_architecture(architecture_data)
