import os
from textx.export import metamodel_export, model_export
from metamodel import create_metamodel
from transformations import apply_transformations

if __name__ == '__main__':
    metamodel = create_metamodel()
    model = metamodel.model_from_file('model.arch')

    # Generate Metamodel and Model diagrams (.dot format)
    os.makedirs('diagrams', exist_ok=True)
    metamodel_export(metamodel, 'diagrams/metamodel.dot')
    model_export(model, 'diagrams/model.dot')

    # Transformations
    apply_transformations(model)
