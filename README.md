# Sistema de Reserva de Voos - PSPD 2025.2

Sistema distribuído de reservas de voos e hotéis usando gRPC, WebSocket e Kubernetes.

## Participantes

<table>
  <tr>
    <td align="center"><a href="https://github.com/leomitx10"><img style="border-radius: 50%;" src="https://avatars.githubusercontent.com/u/90487905?v=4" width="100px;" alt=""/><br /><sub><b>Leandro de Almeida</b></sub></a><br />
    <td align="center"><a href="https://github.com/gaubiela"><img style="border-radius: 50%;" src="https://avatars.githubusercontent.com/u/92053289?v=4" width="100px;" alt=""/><br /><sub><b>Gabriela Alves</b></sub></a><br /><a href="Link git" title="Rocketseat"></a></td>
    <td align="center">
      <td align="center"><a href="https://github.com/LacerdaRenan"><img style="border-radius: 50%;" src="https://avatars.githubusercontent.com/u/88076318?v=4" width="100px;" alt=""/><br /><sub><b>Renan Lacerda</b></sub></a><br /><a href="Link git" title="Rocketseat"></a></td>
    <td align="center">
      <td align="center"><a href="https://github.com/SamuelRicardoDS"><img style="border-radius: 50%;" src="https://avatars.githubusercontent.com/u/89036883?v=4" width="100px;" alt=""/><br /><sub><b>Samuel Ricardo</b></sub></a><br /><a href="Link git" title="Rocketseat"></a></td>
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

## Índice

- [Como Executar](#como-executar)
  - [Docker Compose](#docker-compose-desenvolvimento-rápido)
  - [Kubernetes Multi-Node](#kubernetes-multi-node-trabalho-completo)
- [Monitoramento e Observabilidade](#monitoramento-e-observabilidade)
- [Testes de Carga](#testes-de-carga)
- [Documentação Completa](#documentação-completa)

## Como Executar

### Docker Compose (Desenvolvimento Rápido)

Para desenvolvimento rápido sem Kubernetes:

```bash
# Subir todos os serviços
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar serviços
docker-compose down
```

**Acesse**: http://localhost:3000

---

### Kubernetes Multi-Node (Trabalho Completo)

Para o trabalho completo com cluster multi-node, HPA e Prometheus:

#### 1. Pré-requisitos

**Instalar Minikube**:
```bash
# Linux
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# macOS
brew install minikube

# Windows
choco install minikube

# Verificar
minikube version
```

**Instalar kubectl**:
```bash
# Linux
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl && sudo mv kubectl /usr/local/bin/

# macOS
brew install kubectl

# Windows
choco install kubernetes-cli

# Verificar
kubectl version --client
```

#### 2. Criar Cluster Multi-Node

```bash
# Iniciar cluster com 3 nós (1 master + 2 workers)
minikube start \
  --nodes=3 \
  --cpus=4 \
  --memory=8192 \
  --disk-size=20g \
  --driver=docker

# Verificar nós
kubectl get nodes
# Deve mostrar: minikube (control-plane), minikube-m02, minikube-m03

# Habilitar addons necessários
minikube addons enable metrics-server
minikube addons enable dashboard
```

#### 3. Build e Deploy da Aplicação

```bash
# Configurar Docker para usar daemon do Minikube
eval $(minikube docker-env)

# Build das imagens
docker build -t modulo-a:v1 ./module-a
docker build -t modulo-b:v1 ./module-b
docker build -t modulo-p:v1 ./module-p

# Verificar imagens
docker images | grep modulo

# Deploy dos serviços
kubectl apply -f k8s/deployment-modulo-a.yaml
kubectl apply -f k8s/deployment-modulo-b.yaml
kubectl apply -f k8s/deployment-modulo-p.yaml

# Deploy dos services
kubectl apply -f k8s/service-modulo-a.yaml
kubectl apply -f k8s/service-modulo-b.yaml
kubectl apply -f k8s/service-modulo-p.yaml

# Aguardar pods ficarem prontos
kubectl wait --for=condition=ready pod --all --timeout=120s

# Verificar status
kubectl get pods
kubectl get services
```

#### 4. Configurar Autoscaling (HPA)

```bash
# Aplicar HPAs
kubectl apply -f k8s/hpa-modulo-a.yaml
kubectl apply -f k8s/hpa-modulo-b.yaml
kubectl apply -f k8s/hpa-modulo-p.yaml

# Verificar HPAs
kubectl get hpa

# Monitorar em tempo real
watch -n 2 kubectl get hpa
```

#### 5. Deploy do Prometheus

```bash
# Criar namespace de monitoramento
kubectl apply -f k8s/prometheus-namespace.yaml

# Configurar RBAC (permissões)
kubectl apply -f k8s/prometheus-rbac.yaml

# Aplicar configuração do Prometheus
kubectl apply -f k8s/prometheus-config.yaml

# Deploy do Prometheus
kubectl apply -f k8s/prometheus-deployment.yaml
kubectl apply -f k8s/prometheus-service.yaml

# Verificar
kubectl get all -n monitoring

# Aguardar Prometheus ficar pronto
kubectl wait --for=condition=ready pod -n monitoring -l app=prometheus --timeout=120s
```

#### 6. Acessar Interfaces

```bash
# API Gateway (aplicação)
minikube service api-gateway
# Ou obter URL: minikube service api-gateway --url

# Prometheus (métricas)
minikube service prometheus -n monitoring
# Ou: kubectl port-forward -n monitoring service/prometheus 9090:9090

# Kubernetes Dashboard
minikube dashboard
```

## Monitoramento e Observabilidade

### Prometheus

**Acesso**: http://MINIKUBE_IP:30090

**Queries Úteis**:

```promql
# Taxa de requisições
rate(http_requests_total[5m])

# Latência P95
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Uso de CPU por pod
rate(container_cpu_usage_seconds_total{namespace="default"}[5m])

# Réplicas do HPA
kube_deployment_status_replicas{deployment=~".*service|api-gateway"}
```

**Documentação Completa**: Ver [docs/PROMETHEUS_SETUP.md](docs/PROMETHEUS_SETUP.md)

### Kubernetes Dashboard

```bash
# Abrir dashboard
minikube dashboard

# Monitorar:
# - Pods (status, recursos, logs)
# - Deployments (réplicas)
# - Services (endpoints)
# - HPA (autoscaling)
```

### Métricas CLI

```bash
# Recursos dos nós
kubectl top nodes

# Recursos dos pods
kubectl top pods

# Ordenado por CPU
kubectl top pods --sort-by=cpu

# Logs em tempo real
kubectl logs -f <pod-name>
```

## Testes de Carga

### Setup Inicial

```bash
cd load-tests

# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Verificar
locust --version
```

### Executar Testes

#### Teste Rápido (2 minutos)

```bash
./run_tests.sh quick
```

#### Cenário Específico

```bash
# Ver cenários disponíveis
python scenarios.py

# Executar cenário
./run_tests.sh scenario cenario_1_baseline
./run_tests.sh scenario cenario_2_moderate
./run_tests.sh scenario cenario_3_high_load
```

#### Todos os Cenários

```bash
# ATENÇÃO: Pode levar 30+ minutos
./run_tests.sh all
```

#### Modo Manual (Interface Web)

```bash
# Obter IP do Minikube
export MINIKUBE_IP=$(minikube ip)

# Iniciar Locust com interface web
locust -f locustfile.py --host=http://${MINIKUBE_IP}:30000

# Abrir navegador: http://localhost:8089
# Configurar usuários e duração
# Iniciar teste
```

### Resultados

Após execução, arquivos gerados em `load-tests/results/`:
- `*_report.html` - Relatório visual
- `*_stats.csv` - Estatísticas
- `*_k8s_metrics.txt` - Métricas do Kubernetes

**Documentação Completa**: Ver [load-tests/README.md](load-tests/README.md)

## Documentação Completa

### Documentos Principais

- [KUBERNETES_SETUP.md](docs/KUBERNETES_SETUP.md) - Setup completo do Kubernetes
- [PROMETHEUS_SETUP.md](docs/PROMETHEUS_SETUP.md) - Instalação e uso do Prometheus
- [METODOLOGIA_TESTES.md](docs/METODOLOGIA_TESTES.md) - Metodologia de testes
- [RELATORIO_FINAL.md](docs/RELATORIO_FINAL.md) - Template do relatório final
- [k8s/README.md](k8s/README.md) - Guia de deployment Kubernetes
- [load-tests/README.md](load-tests/README.md) - Guia de testes de carga

### Estrutura do Projeto

```
.
├── module-a/           # Serviço de Voos (Python + gRPC)
├── module-b/           # Serviço de Hotéis (Go + gRPC)
├── module-p/           # API Gateway (Node.js)
├── k8s/                # Manifestos Kubernetes
│   ├── deployment-*.yaml
│   ├── service-*.yaml
│   ├── hpa-*.yaml
│   └── prometheus-*.yaml
├── load-tests/         # Testes de carga (Locust)
│   ├── locustfile.py
│   ├── scenarios.py
│   └── run_tests.sh
├── docs/               # Documentação completa
│   ├── KUBERNETES_SETUP.md
│   ├── PROMETHEUS_SETUP.md
│   ├── METODOLOGIA_TESTES.md
│   └── RELATORIO_FINAL.md
└── README.md           # Este arquivo
```

### Comandos Úteis

**Cluster**:
```bash
kubectl get all                    # Ver todos os recursos
kubectl get nodes                  # Ver nós do cluster
kubectl top nodes                  # Recursos dos nós
kubectl top pods                   # Recursos dos pods
```

**HPA**:
```bash
kubectl get hpa                    # Ver autoscalers
kubectl describe hpa <nome>        # Detalhes do HPA
watch -n 2 kubectl get hpa         # Monitorar em tempo real
```

**Logs e Debug**:
```bash
kubectl logs <pod>                 # Ver logs
kubectl logs -f <pod>              # Logs em tempo real
kubectl describe pod <pod>         # Detalhes do pod
kubectl exec -it <pod> -- /bin/sh  # Shell no pod
```

**Limpeza**:
```bash
kubectl delete -f k8s/             # Deletar todos os recursos
minikube stop                      # Parar cluster
minikube delete                    # Deletar cluster
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
