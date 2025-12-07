import sys
import os

# Adicionar o diretório raiz ao path
root_path = os.path.join(os.path.dirname(__file__), '../..')
sys.path.insert(0, root_path)

# Importar e executar o servidor principal que já tem Prometheus configurado
from voos_server import serve

if __name__ == '__main__':
    serve()
