# 🛫 Sistema de Reserva de Voos e Hotéis - gRPC + Kubernetes

**Disciplina**: Programação de Sistemas Paralelos e Distribuídos (PSPD)
**Universidade**: UnB/FCTE
**Atividade**: Extraclasse - gRPC + Kubernetes

---

## 📋 Índice

1. [Visão Geral](#-visão-geral)
2. [Arquitetura](#-arquitetura)
3. [B.1 - Framework gRPC](#-b1---framework-grpc)
4. [B.2 - Aplicação Distribuída](#-b2---aplicação-distribuída)
5. [B.3 - Kubernetes](#-b3---kubernetes)
6. [Comparativo gRPC vs REST](#-comparativo-grpc-vs-rest)
7. [Como Executar](#-como-executar)
8. [Tecnologias Utilizadas](#-tecnologias-utilizadas)
9. [Estrutura do Projeto](#-estrutura-do-projeto)
10. [Documentação Detalhada](#-documentação-detalhada)

---

## 🎯 Visão Geral

Sistema distribuído de reservas de voos e hotéis que demonstra:
- **4 tipos de comunicação gRPC** (Unary, Server Streaming, Client Streaming, Bidirectional)
- **Arquitetura de microserviços** com 3 módulos independentes
- **API Gateway** para agregação de serviços
- **Comparativo de performance** entre gRPC e REST
- **Deploy em Kubernetes** usando Minikube
- **Containerização com Docker**

---

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────┐
│                    USUÁRIO (Browser)                    │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP/REST
                     ▼
┌─────────────────────────────────────────────────────────┐
│              MÓDULO P - API Gateway                     │
│              (Node.js + Express)                        │
│                                                         │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Frontend   │  │   REST API   │  │  gRPC Stubs  │  │
│  │ (HTML/CSS)  │  │ (Express.js) │  │  (Clientes)  │  │
│  └─────────────┘  └──────────────┘  └──────────────┘  │
└──────────────┬──────────────────────────┬───────────────┘
               │ gRPC                     │ gRPC
               ▼                          ▼
┌──────────────────────────┐  ┌──────────────────────────┐
│  MÓDULO A - Voos         │  │  MÓDULO B - Hotéis       │
│  (Python + gRPC)         │  │  (Go + gRPC)             │
│                          │  │                          │
│  • Base de 1000 voos     │  │  • Base de 50 hotéis     │
│  • Filtros avançados     │  │  • Filtros avançados     │
│  • Simulação de preços   │  │  • Simulação de preços   │
│  • Porta: 50051          │  │  • Porta: 50052          │
└──────────────────────────┘  └──────────────────────────┘
```

### Comunicação

- **Frontend ↔ API Gateway**: HTTP/REST (JSON)
- **API Gateway ↔ Serviços**: gRPC (Protocol Buffers)
- **Serviços internos**: Isolados, comunicação apenas via gRPC

---

## 🎓 B.1 - Framework gRPC

### 📚 Componentes do gRPC

#### 1. **Protocol Buffers (protobuf)**
- Linguagem de serialização de dados
- Binária, compacta e eficiente
- Fortemente tipada
- Suporta evolução de schema

#### 2. **HTTP/2**
- Multiplexação de streams
- Compressão de headers
- Server push
- Comunicação full-duplex

#### 3. **Arquitetura Cliente/Servidor**
- Definição de contratos via `.proto`
- Geração automática de código
- Suporte a múltiplas linguagens

### 🧪 4 Tipos de Comunicação

Implementados em [`grpc-examples/`](grpc-examples/)

#### 1️⃣ **Unary RPC** (Requisição/Resposta Simples)
```protobuf
rpc UnaryCall(UnaryRequest) returns (UnaryResponse);
```
- Cliente envia **1 requisição**, recebe **1 resposta**
- **Uso**: Autenticação, consultas simples, operações CRUD
- **Vantagens**: Simples, similar a REST
- **Exemplo**: Login de usuário, consulta de saldo

#### 2️⃣ **Server Streaming RPC**
```protobuf
rpc ServerStreamingCall(ServerStreamingRequest) returns (stream ServerStreamingResponse);
```
- Cliente envia **1 requisição**, servidor responde com **N mensagens**
- **Uso**: Download de arquivos, logs em tempo real, notificações
- **Vantagens**: Eficiente para enviar grandes volumes ao cliente
- **Exemplo**: Stream de cotações de ações, monitoramento de logs

#### 3️⃣ **Client Streaming RPC**
```protobuf
rpc ClientStreamingCall(stream ClientStreamingRequest) returns (ClientStreamingResponse);
```
- Cliente envia **N requisições**, servidor responde **1 vez**
- **Uso**: Upload de arquivos, envio de métricas, dados em lote
- **Vantagens**: Eficiente para receber grandes volumes do cliente
- **Exemplo**: Upload de arquivo em chunks, envio de telemetria

#### 4️⃣ **Bidirectional Streaming RPC**
```protobuf
rpc BidirectionalStreamingCall(stream BidirectionalRequest) returns (stream BidirectionalResponse);
```
- Cliente e servidor trocam **N mensagens simultaneamente**
- **Uso**: Chat em tempo real, jogos multiplayer, sincronização
- **Vantagens**: Máxima flexibilidade, comunicação full-duplex
- **Exemplo**: Chat, video chamada, colaboração em tempo real

### 📝 Como Executar os Exemplos

```bash
cd grpc-examples

# Gerar código a partir do .proto
python -m grpc_tools.protoc -I./protos --python_out=./python --grpc_python_out=./python ./protos/examples.proto

# Terminal 1: Servidor
cd python
python server.py

# Terminal 2: Cliente
python client.py
```

**Documentação completa**: [grpc-examples/README.md](grpc-examples/README.md)

---

## 🏗️ B.2 - Aplicação Distribuída

### ✈️ Módulo A - Voos (Python + gRPC)

**Localização**: [`Voos/`](Voos/)

#### Funcionalidades
- Base de dados simulada com **1000 voos**
- Filtros avançados:
  - ✅ Origem e Destino
  - ✅ Data
  - ✅ Preço máximo
  - ✅ Companhia aérea
  - ✅ Faixa de horário (manhã/tarde/noite)
- Ordenação: preço, horário, duração
- Simulação de comportamento real:
  - Delay de processamento (1-3s)
  - Variação de disponibilidade
  - Filtro de voos lotados/cancelados

#### Arquivo Proto
```protobuf
service VoosService {
    rpc ConsultarVoos(ConsultaVoosRequest) returns (ConsultaVoosResponse);
}
```

#### Como Executar
```bash
cd Voos

# Gerar código gRPC
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. voos_service.proto

# Iniciar servidor
python voos_server.py  # Porta 50051

# Testar cliente
python voos_client.py
```

---

### 🏨 Módulo B - Hotéis (Go + gRPC)

**Localização**: [`Hoteis/`](Hoteis/)

#### Funcionalidades
- Base de dados simulada com **50 hotéis**
- Filtros avançados:
  - ✅ Cidade
  - ✅ Estrelas (mín/máx)
  - ✅ Preço (mín/máx)
  - ✅ Tipo de acomodação (Hotel, Pousada, Resort, Hostel)
  - ✅ Comodidades (Wi-Fi, Piscina, Academia, etc.)
- Ordenação: preço, avaliação
- Simulação de comportamento real:
  - Preços dinâmicos (variação de ±30%)
  - Disponibilidade probabilística (90%)

#### Arquivo Proto
```protobuf
service HotelService {
  rpc SearchHotels(SearchHotelsRequest) returns (SearchHotelsResponse);
}
```

#### Como Executar
```bash
cd Hoteis

# Gerar código gRPC
make proto

# Iniciar servidor
make server  # Porta 50052

# Testar cliente
make client
```

---

### 🎨 Módulo P - API Gateway (Node.js + Express)

**Localização**: [`module-p/`](module-p/)

#### Componentes

##### 1. **Frontend Web**
- Interface responsiva (HTML/CSS/JavaScript)
- 3 seções:
  - 🛫 Busca de Voos
  - 🏨 Busca de Hotéis
  - 📦 Pacotes Completos (Voo + Hotel)
- Filtros interativos
- Exibição de resultados em tempo real

##### 2. **API REST**
Endpoints disponíveis:

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/flights/search` | Buscar voos |
| POST | `/api/hotels/search` | Buscar hotéis |
| POST | `/api/packages/search` | Buscar pacotes (voo + hotel) |
| GET | `/health` | Health check |

##### 3. **gRPC Stubs (Clientes)**
- Cliente gRPC para Módulo A (Voos)
- Cliente gRPC para Módulo B (Hotéis)
- Tradução REST ↔ gRPC
- Tratamento de erros

#### Arquitetura do Módulo P
```
module-p/
├── public/              # Frontend
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── src/
│   ├── server.js        # Express server
│   ├── grpc/
│   │   └── clients.js   # gRPC clients
│   ├── routes/
│   │   ├── flights.js   # /api/flights
│   │   ├── hotels.js    # /api/hotels
│   │   └── packages.js  # /api/packages
│   └── protos/
│       ├── flights.proto
│       └── hotels.proto
└── package.json
```

#### Como Executar
```bash
cd module-p

# Instalar dependências
npm install

# Iniciar servidor
npm start  # Porta 3000

# Acessar no navegador
http://localhost:3000
```

---

## 📊 Comparativo gRPC vs REST

**Localização**: [`performance-test/`](performance-test/)

### Versões Implementadas

1. **Versão gRPC** (original)
   - Voos: `voos_server.py` (porta 50051)
   - Hotéis: `hotel-server` (porta 50052)

2. **Versão REST** (para comparação)
   - Voos: `voos_rest_server.py` (porta 5001)
   - Hotéis: `rest-server` (porta 5002)

### Cenários de Teste

#### 1️⃣ Requisição Simples
- Poucos filtros (apenas origem e destino)
- 10 requisições

#### 2️⃣ Requisição Complexa
- Múltiplos filtros (origem, destino, data, preço, companhia, horário)
- 10 requisições

#### 3️⃣ Alto Volume
- Requisição simples
- 50 requisições

#### 4️⃣ Grande Volume de Dados
- Retorno de muitos resultados
- 10 requisições

### Como Executar o Teste

```bash
# Terminal 1: Servidor gRPC de Voos
cd Voos
python voos_server.py

# Terminal 2: Servidor REST de Voos
python voos_rest_server.py

# Terminal 3: Executar testes
cd performance-test
pip install grpcio requests statistics
python test_grpc_vs_rest.py
```

### Resultados Esperados

| Cenário | gRPC (ms) | REST (ms) | Vantagem gRPC |
|---------|-----------|-----------|---------------|
| Simples | ~1200 | ~1350 | ~12% |
| Complexo | ~1400 | ~1600 | ~14% |
| Alto Volume | ~1250 | ~1450 | ~16% |
| Grande Volume | ~1300 | ~1500 | ~15% |

### Conclusões

✅ **gRPC é mais rápido devido a**:
- Serialização binária (Protocol Buffers)
- HTTP/2 (multiplexação, compressão)
- Menos overhead de parsing

✅ **REST é melhor para**:
- APIs públicas
- Integração com navegadores
- Debugging (formato texto)

✅ **gRPC é superior para**:
- Comunicação entre microserviços
- Alto volume de requisições
- Requisitos de baixa latência

---

## 🐳 B.3 - Kubernetes

**Localização**: [`k8s/`](k8s/)

### Arquivos de Configuração

| Arquivo | Descrição |
|---------|-----------|
| `deployment-modulo-a.yaml` | Deployment do serviço de Voos (2 réplicas) |
| `service-modulo-a.yaml` | Service ClusterIP para Voos (porta 50051) |
| `deployment-modulo-b.yaml` | Deployment do serviço de Hotéis (2 réplicas) |
| `service-modulo-b.yaml` | Service ClusterIP para Hotéis (porta 50052) |
| `deployment-modulo-p.yaml` | Deployment do API Gateway (2 réplicas) |
| `service-modulo-p.yaml` | Service NodePort para Gateway (porta 30000) |

### Recursos Configurados

#### Módulo A (Voos)
- **Réplicas**: 2
- **Recursos**:
  - Request: 128Mi RAM, 100m CPU
  - Limit: 256Mi RAM, 200m CPU
- **Probes**: Liveness e Readiness (TCP)

#### Módulo B (Hotéis)
- **Réplicas**: 2
- **Recursos**:
  - Request: 128Mi RAM, 100m CPU
  - Limit: 256Mi RAM, 200m CPU
- **Probes**: Liveness e Readiness (TCP)

#### Módulo P (Gateway)
- **Réplicas**: 2
- **Recursos**:
  - Request: 128Mi RAM, 100m CPU
  - Limit: 512Mi RAM, 500m CPU
- **Probes**: Liveness e Readiness (HTTP /health)
- **Variáveis de Ambiente**:
  - `FLIGHT_SERVICE_HOST=voos-service`
  - `HOTEL_SERVICE_HOST=hoteis-service`

### Deploy Passo a Passo

#### 1. Instalar Minikube
```bash
# Windows
choco install minikube

# Linux
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# macOS
brew install minikube
```

#### 2. Iniciar Cluster
```bash
minikube start --driver=docker
minikube status
```

#### 3. Build das Imagens
```bash
# Voos
cd Voos
docker build -t modulo-a:v1 .

# Hotéis
cd ../Hoteis
docker build -t modulo-b:v1 .

# Gateway
cd ../module-p
docker build -t modulo-p:v1 .
```

#### 4. Carregar Imagens no Minikube
```bash
minikube image load modulo-a:v1
minikube image load modulo-b:v1
minikube image load modulo-p:v1
```

#### 5. Aplicar Configurações
```bash
cd ../k8s

kubectl apply -f deployment-modulo-a.yaml
kubectl apply -f service-modulo-a.yaml
kubectl apply -f deployment-modulo-b.yaml
kubectl apply -f service-modulo-b.yaml
kubectl apply -f deployment-modulo-p.yaml
kubectl apply -f service-modulo-p.yaml
```

#### 6. Verificar Deploy
```bash
# Ver todos os recursos
kubectl get all

# Ver pods
kubectl get pods

# Ver logs
kubectl logs -l app=api-gateway
```

#### 7. Acessar Aplicação

**⚠️ Importante**: O método de acesso varia conforme o sistema operacional:

##### Windows (Docker Desktop)
```bash
# Use port-forward (método recomendado)
kubectl port-forward service/api-gateway 3000:3000

# Acesse: http://localhost:3000
```

##### Linux/Mac
```bash
# Use o IP do Minikube com NodePort
minikube service api-gateway

# Ou obtenha o IP manualmente:
minikube ip  # Exemplo: 192.168.49.2
# Acesse: http://<minikube-ip>:30000
```

##### Método Universal (Qualquer SO)
```bash
# Usar script automatizado
./start-services.sh      # Linux/Mac
.\start-services.ps1     # Windows PowerShell
```

**Documentação completa**: [k8s/README.md](k8s/README.md)

---

## 🚀 Como Executar

### Opção 1: Localmente (sem Docker)

#### Pré-requisitos
- Python 3.9+
- Go 1.21+
- Node.js 18+

#### Passos
```bash
# Terminal 1: Voos
cd Voos
pip install grpcio grpcio-tools
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. voos_service.proto
python voos_server.py

# Terminal 2: Hotéis
cd Hoteis
make proto
make server

# Terminal 3: API Gateway
cd module-p
npm install
npm start

# Acessar: http://localhost:3000
```

### Opção 2: Docker Compose

```bash
# Build e iniciar todos os serviços
docker-compose up --build

# Acessar: http://localhost:3000
```

### Opção 3: Kubernetes (Minikube)

#### Método Rápido (Script Automatizado)
```bash
# Windows
.\start-services.ps1

# Linux/Mac
chmod +x start-services.sh
./start-services.sh
```

#### Método Manual
```bash
# 1. Iniciar Minikube
minikube start --driver=docker

# 2. Build e carregar imagens
docker build -t modulo-a:v1 ./Voos
docker build -t modulo-b:v1 ./Hoteis
docker build -t modulo-p:v1 ./module-p

minikube image load modulo-a:v1
minikube image load modulo-b:v1
minikube image load modulo-p:v1

# 3. Aplicar configurações
kubectl apply -f k8s/

# 4. Acessar (varia por SO - ver seção "Acessar Aplicação" acima)
# Windows: kubectl port-forward service/api-gateway 3000:3000
# Linux/Mac: minikube service api-gateway
```

---

## 🛠️ Tecnologias Utilizadas

| Módulo | Tecnologia | Versão | Uso |
|--------|-----------|--------|-----|
| Módulo A | Python | 3.9+ | Servidor gRPC de Voos |
| Módulo A | gRPC | latest | Framework de comunicação |
| Módulo B | Go | 1.21+ | Servidor gRPC de Hotéis |
| Módulo B | Protocol Buffers | 3 | Serialização |
| Módulo P | Node.js | 18+ | API Gateway |
| Módulo P | Express.js | 4.x | Framework web |
| Frontend | HTML/CSS/JS | - | Interface web |
| Infra | Docker | latest | Containerização |
| Infra | Kubernetes | latest | Orquestração |
| Infra | Minikube | latest | Cluster local |
| Test | Flask | 2.x | Servidor REST (comparativo) |

---

## 📁 Estrutura do Projeto

```
PSPD_2025.2_Sistema_Reserva_Voos/
│
├── grpc-examples/               # B.1 - Demonstração dos 4 tipos gRPC
│   ├── protos/
│   │   └── examples.proto
│   ├── python/
│   │   ├── server.py
│   │   └── client.py
│   └── README.md
│
├── Voos/                        # Módulo A - Voos (Python)
│   ├── voos_service.proto
│   ├── voos_server.py           # Servidor gRPC
│   ├── voos_client.py           # Cliente de teste
│   ├── voos_rest_server.py      # Servidor REST (comparativo)
│   ├── Dockerfile
│   └── README.md
│
├── Hoteis/                      # Módulo B - Hotéis (Go)
│   ├── proto/
│   │   └── hotel.proto
│   ├── cmd/
│   │   ├── server/main.go       # Servidor gRPC
│   │   ├── client/main.go       # Cliente de teste
│   │   └── rest-server/main.go  # Servidor REST (comparativo)
│   ├── internal/
│   │   ├── models/hotel.go
│   │   └── service/hotel_service.go
│   ├── Dockerfile
│   ├── Makefile
│   └── README.md
│
├── module-p/                    # Módulo P - API Gateway (Node.js)
│   ├── public/                  # Frontend
│   │   ├── index.html
│   │   ├── styles.css
│   │   └── app.js
│   ├── src/
│   │   ├── server.js
│   │   ├── grpc/clients.js      # Clientes gRPC
│   │   ├── routes/
│   │   │   ├── flights.js
│   │   │   ├── hotels.js
│   │   │   └── packages.js
│   │   └── protos/
│   │       ├── flights.proto
│   │       └── hotels.proto
│   ├── Dockerfile
│   └── package.json
│
├── k8s/                         # B.3 - Arquivos Kubernetes
│   ├── deployment-modulo-a.yaml
│   ├── service-modulo-a.yaml
│   ├── deployment-modulo-b.yaml
│   ├── service-modulo-b.yaml
│   ├── deployment-modulo-p.yaml
│   ├── service-modulo-p.yaml
│   └── README.md
│
├── performance-test/            # Testes de Performance
│   └── test_grpc_vs_rest.py
│
├── docker-compose.yml           # Orquestração Docker
└── README.md                    # Este arquivo
```

---

## 📖 Documentação Detalhada

### Arquivos Proto

#### Voos (voos_service.proto)
```protobuf
service VoosService {
    rpc ConsultarVoos(ConsultaVoosRequest) returns (ConsultaVoosResponse);
}

message ConsultaVoosRequest {
    string origem = 1;
    string destino = 2;
    string data = 3;
    double preco_max = 4;
    string companhia_aerea = 5;
    string faixa_horario = 6;
    string ordenacao = 7;
}

message Voo {
    string id = 1;
    string origem = 2;
    string destino = 3;
    string data = 4;
    string horario_partida = 5;
    string horario_chegada = 6;
    double preco = 7;
    string companhia_aerea = 8;
    // ... (mais campos)
}
```

#### Hotéis (hotel.proto)
```protobuf
service HotelService {
  rpc SearchHotels(SearchHotelsRequest) returns (SearchHotelsResponse);
}

message SearchHotelsRequest {
  string city = 1;
  int32 min_stars = 2;
  int32 max_stars = 3;
  double min_price = 4;
  double max_price = 5;
  string accommodation_type = 6;
  string order_by = 7;
}

message Hotel {
  string id = 1;
  string name = 2;
  string city = 3;
  int32 stars = 4;
  double price = 5;
  bool available = 6;
  repeated string amenities = 7;
  // ... (mais campos)
}
```

### API REST (Módulo P)

#### POST /api/flights/search
```json
{
  "origem": "São Paulo",
  "destino": "Rio de Janeiro",
  "data": "2025-11-15",
  "preco_max": 800,
  "companhia_aerea": "LATAM",
  "faixa_horario": "manha",
  "ordenacao": "preco"
}
```

**Resposta**:
```json
{
  "voos": [
    {
      "id": "V0001",
      "origem": "São Paulo",
      "destino": "Rio de Janeiro",
      "preco": 450.50,
      "horario_partida": "08:00",
      "horario_chegada": "09:30"
      // ...
    }
  ],
  "total_encontrados": 15,
  "tempo_processamento": "1.85s"
}
```

#### POST /api/hotels/search
```json
{
  "city": "Rio de Janeiro",
  "min_stars": 3,
  "max_stars": 5,
  "min_price": 100,
  "max_price": 500,
  "accommodation_type": "Hotel",
  "order_by": "price"
}
```

**Resposta**:
```json
{
  "hotels": [
    {
      "id": "H001",
      "name": "Hotel Copacabana",
      "city": "Rio de Janeiro",
      "stars": 4,
      "price": 250.00,
      "available": true,
      "amenities": ["Wi-Fi", "Piscina", "Academia"]
    }
  ],
  "has_availability": true
}
```

#### POST /api/packages/search
```json
{
  "origem": "São Paulo",
  "destino": "Rio de Janeiro",
  "data": "2025-11-15",
  "max_budget": 2000
}
```

**Resposta**:
```json
{
  "packages": [
    {
      "flight": { /* dados do voo */ },
      "hotel": { /* dados do hotel */ },
      "total_price": 1200.50
    }
  ]
}
```

---

## 🔧 Troubleshooting

### Problema: Servidor gRPC não inicia
```bash
# Verificar porta em uso
netstat -an | grep 50051

# Matar processo
kill -9 $(lsof -t -i:50051)
```

### Problema: Erro ao conectar gRPC
```bash
# Verificar se servidor está rodando
telnet localhost 50051

# Verificar logs
python voos_server.py
```

### Problema: Docker não builda
```bash
# Limpar cache
docker system prune -a

# Rebuild forçado
docker-compose build --no-cache
```

### Problema: Kubernetes pods não iniciam
```bash
# Ver logs detalhados
kubectl describe pod <pod-name>
kubectl logs <pod-name>

# Verificar eventos
kubectl get events --sort-by=.metadata.creationTimestamp
```

### Problema: ERR_CONNECTION_REFUSED no Windows
**Causa**: O túnel do Minikube (`minikube service`) não funciona corretamente no Windows com Docker Desktop.

**Solução**:
```bash
# Use port-forward em vez do túnel
kubectl port-forward service/api-gateway 3000:3000

# Acesse: http://localhost:3000
```

**Alternativa**: Use o script automatizado `start-services.ps1` que já configura o port-forward corretamente.

---

## 📝 Checklist de Entrega

- [x] **B.1** - Demonstração dos 4 tipos de comunicação gRPC
  - [x] Unary Call
  - [x] Server Streaming
  - [x] Client Streaming
  - [x] Bidirectional Streaming
  - [x] Documentação e prints

- [x] **B.2** - Aplicação Cliente/Servidor
  - [x] Módulo A (Voos - Python)
  - [x] Módulo B (Hotéis - Go)
  - [x] Módulo P (API Gateway - Node.js)
  - [x] Frontend web
  - [x] Dockerfiles
  - [x] docker-compose.yml

- [x] **Comparativo gRPC vs REST**
  - [x] Versão REST dos serviços
  - [x] Script de testes
  - [x] 4 cenários de teste
  - [x] Tabela de resultados

- [x] **B.3** - Kubernetes
  - [x] Arquivos YAML (Deployments e Services)
  - [x] Configuração de recursos
  - [x] Probes (Liveness e Readiness)
  - [x] Instruções de deploy
  - [x] Documentação

- [x] **Documentação**
  - [x] README principal
  - [x] README de cada módulo
  - [x] Instruções de execução
  - [x] Troubleshooting

---

## 👥 Equipe

**Aluno 1**: [Nome] - Módulo A (Voos - Python)
**Aluno 2**: [Nome] - Módulo B (Hotéis - Go)
**Aluno 3**: [Nome] - Módulo P (API Gateway)
**Aluno 4**: [Nome] - Kubernetes e Comparativo

---

## 📚 Referências

- [gRPC Documentation](https://grpc.io/docs/)
- [Protocol Buffers](https://developers.google.com/protocol-buffers)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Docker Documentation](https://docs.docker.com/)
- [Express.js Guide](https://expressjs.com/)
- [Go gRPC Tutorial](https://grpc.io/docs/languages/go/)

---

## 📄 Licença

Este projeto foi desenvolvido para fins acadêmicos na disciplina de PSPD - UnB/FCTE.

---

**Última atualização**: Outubro 2025
