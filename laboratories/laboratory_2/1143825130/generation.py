from metamodel import create_metamodel
from transformations import apply_transformations

if __name__ == "__main__":

    metamodel = create_metamodel()
    model = metamodel.model_from_file("model.arch")
    # Will be used by load balancer
    backend_replicas = 5
    apply_transformations(model, backend_replicas)
