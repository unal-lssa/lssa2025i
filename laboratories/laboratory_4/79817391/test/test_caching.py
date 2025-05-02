import requests

from logger import setup_logger

logger = setup_logger("Test cache", "test_cache.log")
      
LOAD_BALANCER_URL = "http://127.0.0.1:8000"

def test_caching():
    """Prueba el caché realizando solicitudes repetidas.

    Este test verifica que la primera solicitud a la URL no esté en caché
    y que las solicitudes posteriores utilicen el caché.
    """
    print_titulo()
    
    # Limpia el caché para las pruebas
    url = f"{LOAD_BALANCER_URL}/clean"
    
    print_subtitulo("LIMPIAR EL CACHÉ PARA PRUEBA LIMPIA")
    
    logger.info(f"1. Llamando al endpoint: [ {url} ] para limpiar el caché")
        
    clean_cache = requests.post(url).json()
    logger.info(f"2. Respuesta limpiar caché: [ {clean_cache} ]\n")
    
    print_subtitulo("REALIZAR EL PRIMER LLAMADO AL BALANCEADOR")
    
    url = f"{LOAD_BALANCER_URL}/data"
        
    logger.info(f"3. Llamando por primera vez al balanceador de carga en el endpoint: [ {url} ]")  
    first_response = requests.get(url).json()
    cached = first_response['cached']
    
    logger.info(f"4. Respuesta del primer llamado 'cached': [ {first_response['cached']} ]")    
    assert not cached, "La primera respuesta no debería estar en caché."
    logger.info(f"4.1 Primer llamado satisfactorio ya que el caché está vacío\n")    

    print_subtitulo("REALIZAR EL SEGUNDO LLAMADO AL BALANCEADOR")
    logger.info(f"5. Segunda respuesta del caché [ {url} ] el cual debe estar vacío: [ {cached} ]")
    second_response = requests.get(url).json()
    
    logger.info(f"6. Segunda respuesta: [ {second_response} ]")
    assert second_response['data'], "La segunda respuesta debería estar en caché."

def print_titulo():
    
    frame = "+" * 100
    logger.info(f"""
+{frame}+

 >> Este test prueba el caché realizando solicitudes repetidas.
    
    Por lo tanto, se verifica que la primera solicitud a la URL no esté en caché
    y que las solicitudes posteriores utilicen el caché.
    
    Pasos del código:
    
    1. Llamando al endpoint: http://127.0.0.1:8000/clean para limpiar el caché
    2. Respuesta limpiar caché: [ {{'cache_clean': True, 'data': {''}'}} ]
    3. Llamando por primera vez al balanceador de carga en el endpoint: http://127.0.0.1:8000/data
    4. Respuesta del primer llamado 'cached': False
    4.1 Primer llamado satisfactorio ya que el caché estará vacío
    5. Segunda respuesta del caché http://127.0.0.1:8000/data el cual no debe estar vacío: False
    6. Segunda respuesta: 'cached': True, 'data': 'Fetched fresh data from DB'
    
    Se están utilizando assert para verificar el comportamiento esperado de las respuestas.
    7. Se utiliza el logger para registrar la información de las respuestas.
    8. Si la condición evaluada es False, lanza una excepción del tipo AssertionError.  
      
+{frame}+
    """)

def print_subtitulo(msg):
    
    frame = "-" * 50
    logger.info(f"""
{frame}
  {msg} 
{frame}
    """)

if __name__ == "__main__":
    test_caching()
