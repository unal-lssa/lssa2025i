import os
from textx import metamodel_from_file
from textx.export import metamodel_export, model_export

# Función para generar y convertir gráficos
def generate_graph(input_file, output_file, is_metamodel=True):
    # Cargar metamodelo
    mm = metamodel_from_file('arch.tx')
    
    if is_metamodel:
        # Exportar metamodelo
        metamodel_export(mm, f"{output_file}.dot")
    else:
        # Cargar modelo
        model = mm.model_from_file(input_file)
        # Exportar modelo
        model_export(model, f"{output_file}.dot")
    
    # Convertir a PNG usando Graphviz
    try:
        # Ejecutar el comando dot
        result = os.system(f"dot -Tpng {output_file}.dot -o {output_file}.png")
        if result == 0:
            print(f"Gráfico generado: {output_file}.png")
        else:
            print("Error al generar el gráfico. Verifica que Graphviz esté instalado y configurado correctamente.")
    except Exception as e:
        print(f"Ocurrió un error al ejecutar el comando dot: {e}")


 

# Generar gráfico del metamodelo
generate_graph(None, "metamodel", is_metamodel=True)

# Generar gráfico del modelo
generate_graph('model.arch', "model", is_metamodel=False)