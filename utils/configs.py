import sys
import yaml

# 1. Ler as configurações do arquivo YAML
def ler_config_yaml(config_path: str='./utils/config.yaml') -> object:
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file) or {}
    except FileNotFoundError:
        print(f'O arquivo de configuração {config_path} não foi encontrado.')
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f'Erro ao fazer o parsing do arquivo YAML: {e}')
        sys.exit(1)
    except Exception as e:
        print(f'Error ao ler o arquivo de configuração {config_path}: {e}')
        sys.exit(1)
    return config