## Comandos para rodar o projeto

### Serviço de Hotéis

1. **Instalar as dependências do Go**:
   ```bash
   go mod tidy
   ```
   _Baixa as dependências necessárias para o serviço de Hotéis._

2. **Iniciar o servidor de Hotéis**:
   ```bash
   go run cmd/server/main.go
   ```
   _Inicia o servidor gRPC para o serviço de Hotéis._

3. **Executar o cliente de Hotéis**:
   ```bash
   go run cmd/client/main.go
   ```
   _Executa o cliente para interagir com o servidor de Hotéis._