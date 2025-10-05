# Sistema de Reserva de Voos - PSPD 2025.2

Sistema distribuído de reservas de voos e hotéis usando gRPC, WebSocket e Kubernetes.

## Participantes

<table>
  <tr>
    <td align="center"><a href="https://github.com/leomitx10"><img style="border-radius: 50%;" src="https://avatars.githubusercontent.com/u/90487905?v=4" width="100px;" alt=""/><br /><sub><b>Leandro de Almeida</b></sub></a><br />
    <td align="center"><a href="https://github.com/gaubiela"><img style="border-radius: 50%;" src="https://avatars.githubusercontent.com/u/92053289?v=4" width="100px;" alt=""/><br /><sub><b>Gabriela Alves</b></sub></a><br /><a href="Link git" title="Rocketseat"></a></td>
    <td align="center">
  </tr>
</table>


## Arquitetura

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │ HTTP/WebSocket
       ▼
┌─────────────────┐
│  API Gateway    │
│   (Node.js)     │
│   Porta 3000    │
└────────┬────────┘
         │ gRPC
    ┌────┴────┐
    ▼         ▼
┌─────────┐  ┌──────────┐
│  Voos   │  │  Hotéis  │
│ (Python)│  │   (Go)   │
│ :50051  │  │  :50052  │
└─────────┘  └──────────┘
```

## Funcionalidades gRPC

- **Unary RPC**: Busca de voos e hotéis
- **Server Streaming**: Monitoramento de voo em tempo real
- **Client Streaming**: Finalização de compra
- **Bidirectional Streaming**: Chat de suporte via WebSocket

## Como Executar

### Docker Compose (Recomendado)

```bash
# Subir todos os serviços
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar serviços
docker-compose down
```

**Acesse**: http://localhost:3000

### Kubernetes/Minikube

#### Instalação do Minikube (se necessário)

```bash
# Linux
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# macOS
brew install minikube

# Windows
choco install minikube

# Verificar instalação
minikube version
```

#### Instalar kubectl (se necessário)

```bash
# Linux (snap)
sudo snap install kubectl --classic

# macOS
brew install kubectl

# Windows
choco install kubernetes-cli

# Verificar instalação
kubectl version --client
```

#### Executar no Minikube

```bash
# Iniciar Minikube
minikube start

# Aplicar manifestos
kubectl apply -f k8s/

# Verificar status
kubectl get pods
kubectl get services

# Acessar aplicação
minikube service api-gateway --url
```

**Acesse**: URL retornada pelo comando acima (ex: http://192.168.49.2:30000)

## Testes de Performance

### Instalação

```bash
cd performance-test
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Compilar Protos

```bash
# Compilar protos de voos
venv/bin/python -m grpc_tools.protoc \
  -I../module-a/proto \
  --python_out=../module-a/proto \
  --grpc_python_out=../module-a/proto \
  ../module-a/proto/voos_service.proto

# Compilar protos de hotel
venv/bin/python -m grpc_tools.protoc \
  -I../module-b/proto \
  --python_out=../module-b/proto \
  --grpc_python_out=../module-b/proto \
  ../module-b/proto/hotel.proto
```

### Executar Testes

```bash
# Teste básico
venv/bin/python test_grpc_vs_rest.py

```

## Exemplos gRPC

O diretório `grpc-examples/` contém exemplos didáticos dos 4 tipos de comunicação gRPC:

### Instalação

```bash
cd grpc-examples
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Compilar protos
python -m grpc_tools.protoc -I./protos --python_out=./python --grpc_python_out=./python ./protos/examples.proto
```

### Executar Exemplos

```bash
# Terminal 1: Servidor
cd python
python server.py

# Terminal 2: Cliente
cd python
python client.py
```

## Tecnologias

- **Python 3.9** + gRPC - Serviço de Voos
- **Go 1.21** + gRPC - Serviço de Hotéis  
- **Node.js** + Express - API Gateway
- **WebSocket** - Chat em tempo real
- **Docker** + **Kubernetes** - Deployment

## Funcionalidades

- Busca de voos e hotéis
- Pacotes combinados
- Carrinho de compras
- Monitoramento em tempo real
- Chat de suporte

---

**Projeto PSPD 2025.2 - UnB**
