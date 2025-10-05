# Módulo de Voos (Python + gRPC)

Serviço de consulta e monitoramento de voos usando gRPC.

## 📁 Estrutura do Projeto

```
module-a/
├── proto/                    # Definições Protocol Buffers
│   ├── voos_service.proto   # Contrato gRPC
│   ├── voos_service_pb2.py  # (gerado)
│   └── voos_service_pb2_grpc.py  # (gerado)
├── internal/                 # Código interno (futuro)
│   ├── models/              # Modelos de dados
│   └── service/             # Lógica de negócio
├── cmd/                     # Executáveis
│   ├── server/              # Servidor gRPC
│   │   └── main.py
│   └── client/              # Cliente de teste
│       └── main.py
├── Dockerfile               # Container Docker
├── requirements.txt         # Dependências Python
└── README.md               # Este arquivo
```

## 🚀 Como Executar

### 1. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 2. Compilar Proto Files (se necessário)

```bash
cd proto
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. voos_service.proto
```

### 3. Iniciar o Servidor gRPC

```bash
python cmd/server/main.py
```

O servidor estará disponível em `localhost:50051`

### 4. Testar com Cliente

```bash
python cmd/client/main.py
```

## 🐳 Docker

### Build

```bash
docker build -t voos-service .
```

### Run

```bash
docker run -p 50051:50051 voos-service
```

## 🔌 Tipos de Comunicação gRPC Implementados

- **Unary RPC**: `ConsultarVoos` - Busca de voos com filtros
- **Server Streaming RPC**: `MonitorarVoo` - Monitoramento em tempo real
- **Bidirectional Streaming RPC**: `ChatSuporte` - Chat de suporte

## 📡 Endpoints gRPC

### ConsultarVoos (Unary)
Busca voos com filtros opcionais.

### MonitorarVoo (Server Streaming)
Monitora status de um voo em tempo real.

### ChatSuporte (Bidirectional Streaming)
Chat de suporte em tempo real.
