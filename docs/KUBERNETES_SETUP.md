# Documentação Completa do Cluster Kubernetes

## Índice

1. [Visão Geral](#visão-geral)
2. [Arquitetura do Cluster](#arquitetura-do-cluster)
3. [Ferramentas Utilizadas](#ferramentas-utilizadas)
4. [Instalação Passo a Passo](#instalação-passo-a-passo)
5. [Configurações dos Recursos](#configurações-dos-recursos)
6. [Autoscaling (HPA)](#autoscaling-hpa)
7. [Monitoramento](#monitoramento)
8. [Troubleshooting](#troubleshooting)

## Visão Geral

Este documento descreve a montagem completa do cluster Kubernetes para o Sistema de Reservas de Voos, incluindo:

- **1 nó mestre (control plane)**: Gerencia o cluster
- **Mínimo 2 worker nodes**: Executam as aplicações (simulados com Minikube multi-node ou K3s)
- **Interface web**: Kubernetes Dashboard
- **Autoscaling**: Horizontal Pod Autoscaler (HPA)
- **Monitoramento**: Prometheus + métricas do Kubernetes

## Arquitetura do Cluster

```
┌─────────────────────────────────────────────────────────────┐
│                    KUBERNETES CLUSTER                        │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌───────────────────────────────────────────────────┐      │
│  │           CONTROL PLANE (Master Node)              │      │
│  │  - API Server                                      │      │
│  │  - Scheduler                                       │      │
│  │  - Controller Manager                              │      │
│  │  - etcd (cluster state)                            │      │
│  └───────────────────────────────────────────────────┘      │
│                          │                                    │
│                          ▼                                    │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                  WORKER NODES                         │   │
│  │                                                        │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │   │
│  │  │ Worker 1     │  │ Worker 2     │  │ Worker 3   │ │   │
│  │  │              │  │              │  │ (opcional) │ │   │
│  │  │ - kubelet    │  │ - kubelet    │  │            │ │   │
│  │  │ - kube-proxy │  │ - kube-proxy │  │            │ │   │
│  │  │ - container  │  │ - container  │  │            │ │   │
│  │  │   runtime    │  │   runtime    │  │            │ │   │
│  │  └──────────────┘  └──────────────┘  └────────────┘ │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              NAMESPACES                              │    │
│  │                                                       │    │
│  │  ┌─────────────┐  ┌──────────────┐                  │    │
│  │  │  default    │  │  monitoring  │                  │    │
│  │  │             │  │              │                  │    │
│  │  │ - API GW    │  │ - Prometheus │                  │    │
│  │  │ - Voos Svc  │  │              │                  │    │
│  │  │ - Hoteis    │  │              │                  │    │
│  │  └─────────────┘  └──────────────┘                  │    │
│  └─────────────────────────────────────────────────────┘    │
└───────────────────────────────────────────────────────────────┘
```

## Ferramentas Utilizadas

### Minikube

**O que é?**
Ferramenta para executar Kubernetes localmente. Cria uma VM ou container com um cluster Kubernetes.

**Por que usar?**
- Ambiente de desenvolvimento
- Fácil setup
- Suporte a multi-node (simula cluster real)
- Addons integrados (dashboard, metrics-server, etc.)

**Instalação**:
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

### kubectl

**O que é?**
CLI para interagir com clusters Kubernetes.

**Instalação**:
```bash
# Linux
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/

# macOS
brew install kubectl

# Windows
choco install kubernetes-cli

# Verificar
kubectl version --client
```

### Docker

**O que é?**
Container runtime usado pelo Kubernetes.

**Instalação**:
```bash
# Linux (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install docker.io
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER

# macOS
brew install --cask docker

# Windows
choco install docker-desktop

# Verificar
docker --version
```

## Instalação Passo a Passo

### Passo 1: Iniciar Cluster Minikube

#### Opção A: Cluster Single-Node (Simples)

```bash
# Iniciar Minikube com recursos adequados
minikube start \
  --cpus=4 \
  --memory=8192 \
  --disk-size=20g \
  --driver=docker

# Verificar status
minikube status
```

#### Opção B: Cluster Multi-Node (Recomendado para Trabalho)

```bash
# Iniciar com 3 nós (1 control-plane + 2 workers)
minikube start \
  --nodes=3 \
  --cpus=4 \
  --memory=8192 \
  --disk-size=20g \
  --driver=docker

# Verificar nós
kubectl get nodes

# Saída esperada:
# NAME           STATUS   ROLES           AGE   VERSION
# minikube       Ready    control-plane   1m    v1.28.0
# minikube-m02   Ready    <none>          1m    v1.28.0
# minikube-m03   Ready    <none>          1m    v1.28.0
```

**Explicação dos Parâmetros**:
- `--nodes=3`: Cria 3 nós (1 master + 2 workers)
- `--cpus=4`: Aloca 4 CPUs ao cluster
- `--memory=8192`: Aloca 8GB de RAM
- `--disk-size=20g`: Espaço em disco
- `--driver=docker`: Usa Docker como runtime

### Passo 2: Habilitar Addons Necessários

```bash
# Metrics Server (necessário para HPA)
minikube addons enable metrics-server

# Dashboard (interface web)
minikube addons enable dashboard

# Ingress (opcional - para acesso externo)
minikube addons enable ingress

# Verificar addons habilitados
minikube addons list
```

**Por que cada addon?**
- **metrics-server**: Coleta métricas de CPU/memória para autoscaling
- **dashboard**: Interface web para visualização
- **ingress**: Controla acesso externo ao cluster

### Passo 3: Configurar Ambiente Docker

```bash
# Configurar shell para usar Docker do Minikube
eval $(minikube docker-env)

# Verificar
docker ps | grep kube
```

**Importante**: Isso faz o Docker CLI apontar para o daemon Docker dentro do Minikube, permitindo que imagens construídas localmente sejam usadas sem push para registry.

### Passo 4: Build das Imagens Docker

```bash
# Módulo A (Voos - Python)
cd module-a
docker build -t modulo-a:v1 .

# Módulo B (Hotéis - Go)
cd ../module-b
docker build -t modulo-b:v1 .

# Módulo P (API Gateway - Node.js)
cd ../module-p
docker build -t modulo-p:v1 .

# Verificar imagens
docker images | grep modulo
```

### Passo 5: Deploy dos Serviços

```bash
cd ../k8s

# Deployments
kubectl apply -f deployment-modulo-a.yaml
kubectl apply -f deployment-modulo-b.yaml
kubectl apply -f deployment-modulo-p.yaml

# Services
kubectl apply -f service-modulo-a.yaml
kubectl apply -f service-modulo-b.yaml
kubectl apply -f service-modulo-p.yaml

# Verificar
kubectl get deployments
kubectl get services
kubectl get pods
```

### Passo 6: Configurar HPA (Horizontal Pod Autoscaler)

```bash
# Aplicar HPAs
kubectl apply -f hpa-modulo-a.yaml
kubectl apply -f hpa-modulo-b.yaml
kubectl apply -f hpa-modulo-p.yaml

# Verificar HPAs
kubectl get hpa

# Observar em tempo real
watch -n 2 kubectl get hpa
```

### Passo 7: Deploy do Prometheus

```bash
# Criar namespace
kubectl apply -f prometheus-namespace.yaml

# RBAC (permissões)
kubectl apply -f prometheus-rbac.yaml

# ConfigMap (configuração)
kubectl apply -f prometheus-config.yaml

# Deployment
kubectl apply -f prometheus-deployment.yaml

# Service
kubectl apply -f prometheus-service.yaml

# Verificar
kubectl get all -n monitoring
```

### Passo 8: Acessar Interfaces Web

```bash
# Dashboard Kubernetes
minikube dashboard

# Prometheus
minikube service prometheus -n monitoring

# API Gateway (aplicação)
minikube service api-gateway
```

## Configurações dos Recursos

### Deployments

Cada deployment define:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: voos-service
spec:
  replicas: 2              # Número inicial de réplicas
  selector:
    matchLabels:
      app: voos-service    # Seletor de pods
  template:
    spec:
      containers:
      - name: voos-service
        image: modulo-a:v1
        imagePullPolicy: Never  # Não busca do registry
        resources:
          requests:          # Recursos garantidos
            memory: "128Mi"
            cpu: "100m"
          limits:            # Recursos máximos
            memory: "256Mi"
            cpu: "200m"
        livenessProbe:       # Verifica se pod está vivo
          tcpSocket:
            port: 50051
          initialDelaySeconds: 10
          periodSeconds: 10
        readinessProbe:      # Verifica se pod está pronto
          tcpSocket:
            port: 50051
          initialDelaySeconds: 5
          periodSeconds: 5
```

**Conceitos Importantes**:

- **Replicas**: Número de pods idênticos
- **Resources Requests**: Recursos mínimos garantidos (scheduler usa isso)
- **Resources Limits**: Máximo que pod pode usar (pod é morto se exceder)
- **Liveness Probe**: Kubernetes reinicia pod se falhar
- **Readiness Probe**: Kubernetes remove pod do Service se não estiver pronto

### Services

Services expõem pods via rede:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: voos-service
spec:
  type: ClusterIP        # Interno ao cluster
  selector:
    app: voos-service    # Seleciona pods por label
  ports:
  - port: 50051          # Porta do service
    targetPort: 50051    # Porta do container
    protocol: TCP
```

**Tipos de Service**:
- **ClusterIP**: Interno (padrão) - usado por Voos e Hotéis
- **NodePort**: Expõe em porta do nó - usado por API Gateway
- **LoadBalancer**: Cloud load balancer (não aplicável em Minikube)

### HPA (Horizontal Pod Autoscaler)

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: voos-service-hpa
spec:
  scaleTargetRef:
    kind: Deployment
    name: voos-service
  minReplicas: 2         # Mínimo de pods
  maxReplicas: 10        # Máximo de pods
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70  # Escala se CPU > 70%
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80  # Escala se Mem > 80%
  behavior:              # Controla velocidade de scaling
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
      - type: Percent
        value: 100       # Dobra número de pods
        periodSeconds: 15
      - type: Pods
        value: 2         # Ou adiciona 2 pods
        periodSeconds: 15
      selectPolicy: Max  # Usa política mais agressiva
    scaleDown:
      stabilizationWindowSeconds: 300  # Aguarda 5min antes de scale down
      policies:
      - type: Percent
        value: 50        # Remove até 50% dos pods
        periodSeconds: 15
```

**Como Funciona o HPA?**

1. Metrics Server coleta CPU/Memory dos pods a cada 15s
2. HPA verifica métricas a cada 15s
3. Se métrica > target:
   - Calcula número desejado de réplicas
   - Aplica política de scale-up
   - Atualiza deployment
4. Se métrica < target:
   - Aguarda stabilization window
   - Aplica política de scale-down

**Fórmula de Cálculo**:
```
desiredReplicas = ceil(currentReplicas * (currentMetric / targetMetric))
```

Exemplo:
- 3 réplicas atuais
- CPU atual: 90%
- CPU target: 70%
- `desiredReplicas = ceil(3 * (90/70)) = ceil(3.86) = 4`

## Autoscaling (HPA)

### Requisitos para HPA Funcionar

1. **Metrics Server** deve estar rodando:
   ```bash
   kubectl get deployment metrics-server -n kube-system
   ```

2. **Resources Requests** devem estar definidos nos Deployments

3. **Carga** deve existir para HPA reagir

### Testando HPA

```bash
# Terminal 1: Monitorar HPA
watch -n 2 kubectl get hpa

# Terminal 2: Monitorar Pods
watch -n 2 kubectl get pods

# Terminal 3: Gerar carga
# (usar load-tests/run_tests.sh)

# Observar:
# - TARGETS: Utilização atual/target
# - REPLICAS: Atual vs desejado
# - AGE: Tempo desde última mudança
```

### Debugging HPA

```bash
# Ver eventos do HPA
kubectl describe hpa voos-service-hpa

# Ver métricas atuais
kubectl top pods

# Ver logs do HPA controller
kubectl logs -n kube-system <hpa-controller-pod>
```

## Monitoramento

### Kubernetes Dashboard

```bash
# Abrir dashboard
minikube dashboard

# Ou obter URL
minikube dashboard --url
```

**O que monitorar**:
- Pods: Status, restarts, recursos
- Deployments: Réplicas disponíveis
- Services: Endpoints
- Nodes: Utilização de recursos

### Métricas CLI

```bash
# Uso de recursos dos nós
kubectl top nodes

# Uso de recursos dos pods
kubectl top pods

# Por namespace
kubectl top pods -n monitoring

# Ordenado por CPU
kubectl top pods --sort-by=cpu

# Ordenado por Memory
kubectl top pods --sort-by=memory
```

### Logs

```bash
# Logs de um pod
kubectl logs <pod-name>

# Logs em tempo real
kubectl logs -f <pod-name>

# Logs anteriores (se pod crashou)
kubectl logs <pod-name> --previous

# Logs de todos os pods de um deployment
kubectl logs -l app=voos-service

# Últimas 100 linhas
kubectl logs <pod-name> --tail=100
```

## Troubleshooting

### Pods não iniciam (Pending)

```bash
# Ver detalhes
kubectl describe pod <pod-name>

# Causas comuns:
# - Recursos insuficientes nos nós
# - Imagem não encontrada
# - PersistentVolume não disponível

# Verificar recursos dos nós
kubectl describe nodes
```

### Pods crashando (CrashLoopBackOff)

```bash
# Ver logs
kubectl logs <pod-name> --previous

# Ver eventos
kubectl get events --sort-by=.metadata.creationTimestamp

# Causas comuns:
# - Erro na aplicação
# - Probe falhando muito cedo
# - Dependências não disponíveis
```

### HPA não escalando

```bash
# Verificar metrics-server
kubectl get deployment metrics-server -n kube-system

# Verificar se há métricas
kubectl top pods

# Verificar configuração do HPA
kubectl describe hpa <hpa-name>

# Causas comuns:
# - Metrics-server não rodando
# - Resources requests não definidos
# - Carga insuficiente
```

### Service não acessível

```bash
# Verificar endpoints
kubectl get endpoints <service-name>

# Sem endpoints? Selector pode estar errado
kubectl describe service <service-name>
kubectl get pods --show-labels

# Verificar conectividade
kubectl run -it --rm debug --image=busybox --restart=Never -- wget -O- <service-name>:<port>
```

### Imagem não encontrada

```bash
# Verificar imagePullPolicy
# Se imagePullPolicy: Always, Kubernetes tentará baixar
# Use imagePullPolicy: Never para imagens locais

# Verificar imagens no Minikube
minikube ssh
docker images

# Recarregar imagem
eval $(minikube docker-env)
docker build -t modulo-a:v1 .
```

## Comandos Úteis

### Gerenciamento de Recursos

```bash
# Aplicar manifesto
kubectl apply -f deployment.yaml

# Deletar recurso
kubectl delete -f deployment.yaml
kubectl delete deployment <name>

# Editar recurso (abre editor)
kubectl edit deployment <name>

# Escalar manualmente
kubectl scale deployment <name> --replicas=5

# Ver YAML de recurso existente
kubectl get deployment <name> -o yaml

# Ver todos os recursos
kubectl get all
```

### Debug

```bash
# Executar comando em pod
kubectl exec <pod-name> -- <command>

# Shell interativo
kubectl exec -it <pod-name> -- /bin/sh

# Port-forward (acesso local)
kubectl port-forward <pod-name> 8080:3000

# Port-forward service
kubectl port-forward service/<service-name> 8080:3000

# Copiar arquivo
kubectl cp <pod-name>:/path/to/file ./local-file
```

### Limpeza

```bash
# Deletar todos os recursos de um diretório
kubectl delete -f k8s/

# Deletar por label
kubectl delete pods -l app=voos-service

# Deletar namespace (e tudo dentro)
kubectl delete namespace monitoring

# Parar Minikube
minikube stop

# Deletar cluster
minikube delete
```

## Referências

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Minikube Documentation](https://minikube.sigs.k8s.io/docs/)
- [HPA Documentation](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)
- Cloud Native DevOps with Kubernetes - O'Reilly
