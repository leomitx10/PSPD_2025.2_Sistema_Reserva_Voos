# Kubernetes Deployment - Sistema de Reservas

## 📋 Pré-requisitos

1. **Minikube instalado**
   ```bash
   # Windows (via Chocolatey)
   choco install minikube

   # Linux
   curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
   sudo install minikube-linux-amd64 /usr/local/bin/minikube

   # macOS
   brew install minikube
   ```

2. **kubectl instalado**
   ```bash
   # Windows
   choco install kubernetes-cli

   # Linux
   curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"

   # macOS
   brew install kubectl
   ```

## 🚀 Deploy Completo

### 1. Iniciar Minikube
```bash
minikube start --driver=docker
minikube status
```

### 2. Build das Imagens Docker
```bash
# Módulo A (Voos - Python)
cd ../Voos
docker build -t modulo-a:v1 .

# Módulo B (Hotéis - Go)
cd ../Hoteis
docker build -t modulo-b:v1 .

# Módulo P (API Gateway - Node.js)
cd ../module-p
docker build -t modulo-p:v1 .
```

### 3. Carregar Imagens no Minikube
```bash
minikube image load modulo-a:v1
minikube image load modulo-b:v1
minikube image load modulo-p:v1
```

### 4. Aplicar Configurações Kubernetes
```bash
cd ../k8s

# Módulo A (Voos)
kubectl apply -f deployment-modulo-a.yaml
kubectl apply -f service-modulo-a.yaml

# Módulo B (Hotéis)
kubectl apply -f deployment-modulo-b.yaml
kubectl apply -f service-modulo-b.yaml

# Módulo P (Gateway)
kubectl apply -f deployment-modulo-p.yaml
kubectl apply -f service-modulo-p.yaml
```

### 5. Verificar Deployments
```bash
# Verificar todos os recursos
kubectl get all

# Verificar pods
kubectl get pods

# Verificar services
kubectl get services

# Verificar deployments
kubectl get deployments
```

### 6. Acessar a Aplicação
```bash
# Obter URL do serviço
minikube service api-gateway --url

# Ou expor diretamente
minikube service api-gateway
```

A aplicação estará disponível em `http://<minikube-ip>:30000`

## 🔍 Comandos Úteis

### Logs
```bash
# Ver logs de um pod específico
kubectl logs <nome-do-pod>

# Ver logs em tempo real
kubectl logs -f <nome-do-pod>

# Logs de todos os pods de um deployment
kubectl logs -l app=voos-service
```

### Describe (Detalhes)
```bash
# Detalhes de um deployment
kubectl describe deployment voos-service

# Detalhes de um pod
kubectl describe pod <nome-do-pod>

# Detalhes de um service
kubectl describe service api-gateway
```

### Escalar Deployments
```bash
# Aumentar número de réplicas
kubectl scale deployment voos-service --replicas=3

# Verificar escalamento
kubectl get deployments
```

### Debug
```bash
# Entrar em um pod
kubectl exec -it <nome-do-pod> -- /bin/sh

# Port-forward para acesso local
kubectl port-forward service/api-gateway 3000:3000
```

### Deletar Recursos
```bash
# Deletar um deployment
kubectl delete deployment voos-service

# Deletar um service
kubectl delete service voos-service

# Deletar tudo de uma vez
kubectl delete -f deployment-modulo-a.yaml
kubectl delete -f service-modulo-a.yaml
```

## 📊 Arquitetura no Kubernetes

```
┌─────────────────────────────────────────┐
│          Kubernetes Cluster             │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │     api-gateway (NodePort)        │ │
│  │     Porta: 30000                  │ │
│  │     Réplicas: 2                   │ │
│  └──────────┬────────────────────────┘ │
│             │                           │
│    ┌────────┴────────┐                 │
│    │                 │                 │
│  ┌─▼──────────┐   ┌─▼──────────┐      │
│  │ voos-svc   │   │ hoteis-svc │      │
│  │ ClusterIP  │   │ ClusterIP  │      │
│  │ :50051     │   │ :50052     │      │
│  │ Réplicas:2 │   │ Réplicas:2 │      │
│  └────────────┘   └────────────┘      │
│                                         │
└─────────────────────────────────────────┘
```

## 🛠️ Troubleshooting

### Pods não iniciam
```bash
# Verificar eventos
kubectl get events --sort-by=.metadata.creationTimestamp

# Verificar logs
kubectl logs <nome-do-pod>

# Verificar descrição
kubectl describe pod <nome-do-pod>
```

### Erro de imagem
```bash
# Verificar se a imagem foi carregada
minikube image ls | grep modulo

# Recarregar imagem
minikube image load modulo-a:v1
```

### Serviço não acessível
```bash
# Verificar serviços
kubectl get svc

# Verificar endpoints
kubectl get endpoints

# Testar porta
kubectl port-forward service/api-gateway 3000:3000
```

## 📈 Monitoramento

### Dashboard do Kubernetes
```bash
minikube dashboard
```

### Métricas
```bash
# Habilitar métricas
minikube addons enable metrics-server

# Ver uso de recursos
kubectl top nodes
kubectl top pods
```

## 🧹 Limpeza

### Deletar tudo
```bash
# Deletar todos os recursos
kubectl delete -f .

# Parar Minikube
minikube stop

# Deletar cluster
minikube delete
```

## 📝 Configurações dos Arquivos

### deployment-modulo-a.yaml
- **Imagem**: modulo-a:v1
- **Porta**: 50051 (gRPC)
- **Réplicas**: 2
- **Resources**: 128Mi-256Mi RAM, 100m-200m CPU

### service-modulo-a.yaml
- **Tipo**: ClusterIP (interno)
- **Porta**: 50051

### deployment-modulo-b.yaml
- **Imagem**: modulo-b:v1
- **Porta**: 50052 (gRPC)
- **Réplicas**: 2
- **Resources**: 128Mi-256Mi RAM, 100m-200m CPU

### service-modulo-b.yaml
- **Tipo**: ClusterIP (interno)
- **Porta**: 50052

### deployment-modulo-p.yaml
- **Imagem**: modulo-p:v1
- **Porta**: 3000 (HTTP)
- **Réplicas**: 2
- **Resources**: 128Mi-512Mi RAM, 100m-500m CPU
- **Variáveis de ambiente**:
  - FLIGHT_SERVICE_HOST=voos-service
  - HOTEL_SERVICE_HOST=hoteis-service

### service-modulo-p.yaml
- **Tipo**: NodePort (externo)
- **Porta**: 3000
- **NodePort**: 30000

## ✅ Checklist de Verificação

- [ ] Minikube iniciado
- [ ] Imagens Docker construídas
- [ ] Imagens carregadas no Minikube
- [ ] Deployments aplicados
- [ ] Services aplicados
- [ ] Todos os pods rodando (kubectl get pods)
- [ ] Serviço acessível (minikube service api-gateway)
- [ ] Aplicação funcionando no navegador
