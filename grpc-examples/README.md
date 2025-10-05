# Demonstração dos 4 Tipos de Comunicação gRPC (B.1)

Este módulo demonstra os 4 tipos fundamentais de comunicação do gRPC.

## 📋 Tipos de Comunicação

### 1. **Unary RPC** (Requisição/Resposta Simples)
- **Como funciona**: Cliente envia uma requisição, servidor envia uma resposta
- **Casos de uso**:
  - Autenticação de usuários
  - Consultas simples de dados
  - Validações
  - Operações CRUD básicas

### 2. **Server Streaming RPC**
- **Como funciona**: Cliente envia uma requisição, servidor responde com stream de mensagens
- **Casos de uso**:
  - Download de arquivos grandes
  - Logs em tempo real
  - Notificações push
  - Transferência de dados volumosos

### 3. **Client Streaming RPC**
- **Como funciona**: Cliente envia stream de requisições, servidor responde uma vez no final
- **Casos de uso**:
  - Upload de arquivos
  - Envio de métricas em lote
  - Agregação de dados
  - Coleta de telemetria

### 4. **Bidirectional Streaming RPC**
- **Como funciona**: Cliente e servidor trocam streams simultaneamente
- **Casos de uso**:
  - Chat em tempo real
  - Jogos multiplayer
  - Sincronização bidirecional
  - Comunicação full-duplex

## 🚀 Como Executar

### Pré-requisitos
```bash
pip install grpcio grpcio-tools
```

### Gerar código a partir do .proto
```bash
cd grpc-examples
python -m grpc_tools.protoc -I./protos --python_out=./python --grpc_python_out=./python ./protos/examples.proto
```

### Executar o servidor
```bash
cd python
python server.py
```

### Executar o cliente (em outro terminal)
```bash
cd python
python client.py
```

## 📊 Comparação dos Tipos

| Tipo | Cliente Envia | Servidor Envia | Latência | Throughput |
|------|---------------|----------------|----------|------------|
| Unary | 1 msg | 1 msg | Baixa | Médio |
| Server Streaming | 1 msg | N msgs | Baixa inicial | Alto |
| Client Streaming | N msgs | 1 msg | Acumulada | Alto |
| Bidirectional | N msgs | N msgs | Variável | Muito Alto |

## 🎯 Conclusões

- **Unary**: Simplicidade e familiaridade (similar a REST)
- **Server Streaming**: Eficiente para enviar grandes volumes ao cliente
- **Client Streaming**: Ideal para receber dados em lote
- **Bidirectional**: Máxima flexibilidade para comunicação em tempo real

## 📝 Logs Esperados

### Servidor:
```
Servidor gRPC Examples rodando na porta 50053
[UNARY] Recebida mensagem: Olá, servidor!
[SERVER STREAMING] Enviando 5 mensagens com prefixo 'LOG'
[CLIENT STREAMING] Recebido #1: Dados-1
[CLIENT STREAMING] Recebido #2: Dados-2
...
[BIDIRECTIONAL] Recebido: Olá
[BIDIRECTIONAL] Recebido: Como vai?
```

### Cliente:
```
1. UNARY CALL - Requisição/Resposta Simples
Enviado: Olá, servidor!
Recebido: Processado: Olá, servidor!

2. SERVER STREAMING - Servidor envia stream
[1] LOG - Mensagem 1/5
[2] LOG - Mensagem 2/5
...
```
