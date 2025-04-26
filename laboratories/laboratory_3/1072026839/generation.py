from metamodel import create_metamodel
from transformations import apply_transformations

if __name__ == '__main__':
    metamodel = create_metamodel() # Metamodeling
    model = metamodel.model_from_file('model.arch') # Modeling
    apply_transformations(model) # Transformations M2T (M2T: Model-to-Text, M2M: Model-to-Model)
