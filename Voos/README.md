# Módulo A - Serviço de Voos (Python + gRPC)

## 📋 Descrição

Serviço gRPC para consulta de voos com filtros avançados e simulação de comportamento real.

## ⚙️ Funcionalidades

### Base de Dados
- **1000 voos simulados** gerados automaticamente
- Múltiplas companhias aéreas (LATAM, GOL, Azul, TAM, Avianca)
- Diversas rotas entre principais cidades brasileiras

### Filtros Disponíveis
- ✅ Origem, Destino, Data
- ✅ Preço Máximo, Companhia Aérea
- ✅ Faixa de Horário (manhã/tarde/noite)
- ✅ Ordenação (preço/horário/duração)

### Simulações Realistas
- Delay de processamento: 1-3 segundos
- Variação de disponibilidade
- Filtro de voos ativos

## 🚀 Comandos para rodar o projeto

### Serviço de Voos (gRPC)

1. **Criar e ativar o ambiente virtual**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/Mac
   # OU
   venv\Scripts\activate     # Windows
   ```

2. **Instalar as dependências**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Gerar código gRPC**:
   ```bash
   python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. voos_service.proto
   ```

4. **Iniciar o servidor gRPC**:
   ```bash
   python voos_server.py
   # Rodará na porta 50051
   ```

5. **Executar o cliente de teste**:
   ```bash
   python voos_client.py
   ```

### Serviço REST (para comparativo)

```bash
pip install flask flask-cors
python voos_rest_server.py
# Rodará na porta 5001
```

## 🐳 Docker

```bash
docker build -t modulo-a:v1 .
docker run -p 50051:50051 modulo-a:v1
```

## 📡 API gRPC

```protobuf
service VoosService {
    rpc ConsultarVoos(ConsultaVoosRequest) returns (ConsultaVoosResponse);
}
```

## 📁 Arquivos

- `voos_service.proto` - Definição gRPC
- `voos_server.py` - Servidor gRPC (porta 50051)
- `voos_client.py` - Cliente de teste
- `voos_rest_server.py` - Servidor REST (porta 5001)
- `Dockerfile` - Containerização