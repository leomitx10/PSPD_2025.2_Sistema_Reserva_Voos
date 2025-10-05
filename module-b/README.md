# Módulo de Hotéis (Go + gRPC)

Serviço de consulta de hotéis e finalização de compras usando gRPC.

## 📁 Estrutura do Projeto

```
module-b/
├── proto/                    # Definições Protocol Buffers
│   ├── hotel.proto          # Contrato gRPC
│   ├── hotel.pb.go          # (gerado)
│   └── hotel_grpc.pb.go     # (gerado)
├── internal/                 # Código interno
│   ├── models/              # Modelos de dados
│   │   └── hotel.go
│   └── service/             # Lógica de serviço gRPC
│       └── hotel_service.go
├── cmd/                     # Executáveis
│   ├── server/              # Servidor gRPC
│   │   └── main.go
│   ├── client/              # Cliente de teste
│   │   └── main.go
│   └── rest-server/         # Servidor REST (opcional)
│       └── main.go
├── Dockerfile               # Container Docker
├── go.mod                   # Dependências Go
├── go.sum                   # Checksums
├── Makefile                 # Comandos úteis
└── README.md               # Este arquivo
```

## 🚀 Como Executar

### 1. Instalar Dependências

```bash
go mod tidy
```

### 2. Compilar Proto Files (se necessário)

```bash
make proto
# ou
protoc --go_out=. --go-grpc_out=. proto/hotel.proto
```

### 3. Iniciar o Servidor gRPC

```bash
go run cmd/server/main.go
```

O servidor estará disponível em `localhost:50052`

### 4. Testar com Cliente

```bash
go run cmd/client/main.go
```

## 🐳 Docker

### Build

```bash
docker build -t hoteis-service .
```

### Run

```bash
docker run -p 50052:50052 hoteis-service
```

## 🔌 Tipos de Comunicação gRPC Implementados

- **Unary RPC**: `SearchHotels` - Busca de hotéis com filtros
- **Client Streaming RPC**: `FinalizarCompra` - Finalização de carrinho
- **Bidirectional Streaming RPC**: `ChatSuporte` - Chat de suporte

## 📡 Endpoints gRPC

### SearchHotels (Unary)
Busca hotéis com filtros opcionais.

### FinalizarCompra (Client Streaming)
Recebe stream de itens do carrinho e retorna código de confirmação.

### ChatSuporte (Bidirectional Streaming)
Chat de suporte em tempo real.
