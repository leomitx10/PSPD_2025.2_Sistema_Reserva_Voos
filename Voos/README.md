## Comandos para rodar o projeto

### Serviço de Voos

1. **Criar e ativar o ambiente virtual**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
   _Cria um ambiente isolado para instalar as dependências._

2. **Instalar as dependências**:
   ```bash
   pip install -r requirements.txt
   ```
   _Instala as bibliotecas necessárias para o serviço de Voos._

3. **Iniciar o servidor de Voos**:
   ```bash
   python3 voos_server.py
   ```
   _Inicia o servidor gRPC para o serviço de Voos._

4. **Executar o cliente de Voos**:
   ```bash
   python3 voos_client.py
   ```
   _Executa o cliente para interagir com o servidor de Voos._