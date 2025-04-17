import os 
from textx import metamodel_from_file 

def create_metamodel(): 
    grammar = os.path.join(os.path.dirname(__file__), 'arch.tx') ##Carga archivo de modelo a variable grammar
    return metamodel_from_file(grammar) ##Crea metamodelo a partir de la gramática definida en el archivo arch.tx y lo retorna