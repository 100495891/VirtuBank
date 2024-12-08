import logging

# Configuramos el log
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='log_criptografia.log',
    filemode='a'
)
def get_logger(nombre):
    return logging.getLogger(nombre)