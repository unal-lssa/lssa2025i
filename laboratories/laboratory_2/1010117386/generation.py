from metamodel import create_metamodel
from transformations import apply_transformations

if __name__ == '__main__':
    metamodel = create_metamodel()
    model = metamodel.model_from_file('model.arch')
    apply_transformations(model)