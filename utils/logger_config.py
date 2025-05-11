import logging
from utils.configs import ler_config_yaml

logger = logging.getLogger(__name__)

# Configurar sistema de logging
def configurar_logging() -> None:
    loggign_config = ler_config_yaml().get('logging', {})
    
    if not loggign_config:
        print('Nenhuma configuração de logging encontrada. Utilizando configuração padrão.')
        return
    
    log_level = getattr(logging, loggign_config.get('level', 'INFO').upper(), logging.INFO)
    log_format = loggign_config.get('format', '%(asctime)s - %(levelname)s - %(message)s')
    output_file = loggign_config.get('file', None)

    # Determinando o destino dos logs de acordo com o valor de `output_file`
    handlers = []
    if output_file:
        handlers.append(logging.FileHandler(output_file))
    else:
        handlers.append(logging.StreamHandler())

    # Configuração do logging
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=handlers
    )