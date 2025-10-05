# Sistema de Reserva de Voos - PSPD 2025.2

Sistema distribuído de reservas de voos e hotéis usando gRPC e Kubernetes.

## 🏗️ Arquitetura

```
┌─────────────┐
│   Browser   │
│  (Cliente)  │
└──────┬──────┘
       │ HTTP/REST
       │ WebSocket (Chat)
       │ SSE (Monitoring)
       ▼
┌─────────────────┐
│  API Gateway    │
│   (Node.js)     │
│   Porta 3000    │
└────────┬────────┘
         │ gRPC
    ┌────┴────┐
    │         │
    ▼         ▼
┌─────────┐  ┌──────────┐
│  Voos   │  │  Hotéis  │
│ (Python)│  │   (Go)   │
│ :50051  │  │  :50052  │
└─────────┘  └──────────┘
```

## 📁 Estrutura do Projeto

```
.
├── module-a/                # Módulo A - Voos (Python + gRPC)
│   ├── proto/              # Protocol Buffers
│   ├── cmd/                # Executáveis (server, client)
│   └── internal/           # Código interno
│
├── module-b/                # Módulo B - Hotéis (Go + gRPC)
│   ├── proto/              # Protocol Buffers
│   ├── cmd/                # Executáveis (server, client)
│   └── internal/           # Código interno
│
├── module-p/                # Módulo P - API Gateway (Node.js)
│   ├── src/                # Código fonte
│   │   ├── routes/         # Rotas REST
│   │   └── websocket/      # WebSocket handlers
│   └── public/             # Frontend
│
├── performance-test/        # Testes de performance gRPC vs REST
│
├── k8s/                     # Manifestos Kubernetes
│
├── docker-compose.yml       # Orquestração Docker
└── README.md               # Este arquivo
```

## 🔌 Tipos de Comunicação gRPC

O projeto demonstra os **4 tipos de comunicação gRPC**:

### 1. Unary RPC (Request → Response)
- **Voos**: `ConsultarVoos` - Busca de voos
- **Hotéis**: `SearchHotels` - Busca de hotéis

### 2. Server Streaming RPC (1 Request → N Responses)
- **Voos**: `MonitorarVoo` - Monitoramento em tempo real de status do voo

### 3. Client Streaming RPC (N Requests → 1 Response)
- **Hotéis**: `FinalizarCompra` - Envio de itens do carrinho

### 4. Bidirectional Streaming RPC (N Requests ↔ N Responses)
- **Voos**: `ChatSuporte` - Chat de suporte
- **Hotéis**: `ChatSuporte` - Chat de suporte

## 🚀 Como Executar

### Resumo das Opções

| Opção | Quando Usar | Complexidade | Requisitos |
|-------|-------------|--------------|------------|
| **Docker Compose** | Desenvolvimento rápido, sem configuração | ⭐ Fácil | Docker |
| **Kubernetes** | Ambiente de produção, orquestração | ⭐⭐⭐ Avançado | Minikube/K8s |
| **Local** | Desenvolvimento com debug, aprendizado | ⭐⭐ Médio | Python, Go, Node.js |

---

### Opção 1: Docker Compose (Recomendado)

```bash
# Subir todos os serviços
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar serviços
docker-compose down
```

Acesse: http://localhost:3000

### Opção 2: Kubernetes/Minikube

```bash
# Iniciar Minikube
minikube start

# Aplicar manifestos
kubectl apply -f k8s/

# Ver status
kubectl get pods
kubectl get services

# Acessar aplicação
minikube service api-gateway-service --url
```

### Opção 3: Executar Localmente

#### Método Automático (Recomendado)

**Windows:**
```powershell
.\setup-local.ps1
```

**Linux/Mac:**
```bash
chmod +x setup-local.sh
./setup-local.sh
```

#### Método Manual

##### Passo 1: Instalar Dependências e Compilar Protos

**Python (module-a):**
```bash
cd module-a
pip install -r requirements.txt
python -m grpc_tools.protoc -I./proto --python_out=./proto --grpc_python_out=./proto proto/voos_service.proto
```

**Go (module-b):**
```bash
cd module-b
go mod tidy

# Instalar plugins protoc Go (uma vez)
go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest

# Compilar protos (precisa ter protoc instalado)
# Windows: baixe de https://github.com/protocolbuffers/protobuf/releases
# Linux/Mac: sudo apt install protobuf-compiler (ou brew install protobuf)
protoc --go_out=. --go_opt=paths=source_relative --go-grpc_out=. --go-grpc_opt=paths=source_relative proto/hotel.proto
```

**Node.js (module-p):**
```bash
cd module-p
npm install
```

#### Passo 2: Executar os Serviços (3 terminais separados)

**Terminal 1 - Voos:**
```bash
cd module-a
python cmd/server/main.py
```

**Terminal 2 - Hotéis:**
```bash
cd module-b
go run cmd/server/main.go
```

**Terminal 3 - Gateway:**
```bash
cd module-p
npm start
```

Acesse: http://localhost:3000

> **Nota**: Se não conseguir instalar `protoc`, os arquivos `.pb.go` e `_pb2.py` já estão incluídos no repositório. Apenas certifique-se de que estão atualizados.

#### Troubleshooting Local

**Erro: "porta já em uso"**
```bash
# Parar containers Docker se estiverem rodando
docker-compose down

# Windows - verificar portas
netstat -ano | findstr "50051"
netstat -ano | findstr "50052"
netstat -ano | findstr "3000"

# Linux/Mac - verificar portas
lsof -i :50051
lsof -i :50052
lsof -i :3000
```

**Erro: "protoc not found"**
- Use o script `setup-local.ps1` (Windows) ou `setup-local.sh` (Linux/Mac)
- Ou baixe manualmente de: https://github.com/protocolbuffers/protobuf/releases

**Erro: "cannot import name 'runtime_version'"**
```bash
cd module-a
pip install --upgrade protobuf grpcio grpcio-tools
python -m grpc_tools.protoc -I./proto --python_out=./proto --grpc_python_out=./proto proto/voos_service.proto
```

**Erro Go: "undefined: pb.ItemCarrinho"**
```bash
cd module-b
go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest
protoc --go_out=. --go_opt=paths=source_relative --go-grpc_out=. --go-grpc_opt=paths=source_relative proto/hotel.proto
```

---

## 🧪 Testes de Performance

Compare performance entre gRPC e REST:

```bash
cd performance-test
pip install websocket-client
python test_grpc_vs_rest.py
```

O teste executa 6 cenários demonstrando os 4 tipos de gRPC:
1. Unary RPC - Simples
2. Unary RPC - Complexo
3. Server Streaming RPC
4. Client Streaming RPC
5. Bidirectional Streaming RPC
6. Alto Volume (Stress Test)

## 🛠️ Tecnologias

- **Python 3.9** - Serviço de Voos
- **Go 1.21** - Serviço de Hotéis
- **Node.js** - API Gateway
- **gRPC** - Comunicação entre serviços
- **Protocol Buffers** - Serialização
- **Docker** - Containerização
- **Kubernetes** - Orquestração
- **WebSocket** - Chat em tempo real
- **Server-Sent Events** - Monitoramento

## 📚 Documentação

- [Módulo A - Voos](./module-a/README.md)
- [Módulo B - Hotéis](./module-b/README.md)
- [Módulo P - API Gateway](./module-p/README.md)

## 🎯 Funcionalidades

### Frontend (Web)
- 🔍 Busca de voos e hotéis com filtros
- 📦 Pacotes combinados (voo + hotel)
- 🛒 Carrinho de compras
- 📡 Monitoramento de voo em tempo real
- 💬 Chat de suporte
- 🎨 Interface responsiva

### Backend
- ⚡ Comunicação gRPC de alta performance
- 🔄 REST API via Gateway
- 📊 Geração de dados simulados
- 🏥 Health checks
- 🐳 Containerização completa

## 👥 Equipe

Projeto desenvolvido para a disciplina de PSPD 2025.2

## 📝 Licença

Projeto acadêmico - UnB
