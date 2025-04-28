from metamodel import create_metamodel
from transformations.transformations import extract_architecture_data, generate_architecture
import json # Importa la librería json

if __name__ == '__main__':

    metamodel = create_metamodel()
    model = metamodel.model_from_file('model.arch')
    architecture_data = extract_architecture_data(model)

    # --- Imprimir architecture_data en formato JSON ---
    print("--- Architecture Data (JSON Format) ---")
    # Usamos json.dumps para convertir el diccionario a string JSON
    # indent=2 le dice que use 2 espacios para cada nivel de indentación
    # Esto hace que la estructura sea muy legible.
    print(json.dumps(architecture_data, indent=2))
    print("---------------------------------------")

    # Generar la arquitectura
    generate_architecture(architecture_data)