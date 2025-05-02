import logging

def setup_logger(name, log_file, level=logging.INFO):
    """
    Configura un logger con un formato estándar.

    Args:
        name (str): Nombre del logger.
        log_file (str): Ruta del archivo donde se guardarán los logs.
        level (int): Nivel de registro (INFO, DEBUG, ERROR, etc.).

    Returns:
        logging.Logger: Instancia configurada del logger.
    """
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)

    # Add a StreamHandler to also log to Docker's stdout
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger