# Guia Rápido - Setup Completo do Trabalho

Este guia fornece os comandos essenciais para configurar e executar o trabalho completo em ordem.

## Checklist de Requisitos do Trabalho

- [x] Aplicação baseada em microserviços (P, A, B)
- [x] Comunicação gRPC entre módulos
- [x] Cluster Kubernetes (1 master + 2 workers)
- [x] Autoscaling (HPA)
- [x] Prometheus para monitoramento
- [x] Interface web de monitoramento (Dashboard + Prometheus)
- [x] Ferramenta de teste de carga (Locust)
- [x] Mínimo 5 cenários de teste
- [x] Documentação completa

## Setup Completo - Passo a Passo

### 1. Instalação de Ferramentas

```bash
# Minikube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl && sudo mv kubectl /usr/local/bin/

# Verificar
minikube version
kubectl version --client
```

### 2. Criar Cluster Multi-Node

```bash
# Cluster com 3 nós
minikube start --nodes=3 --cpus=4 --memory=8192 --disk-size=20g --driver=docker

# Habilitar addons
minikube addons enable metrics-server
minikube addons enable dashboard

# Verificar
kubectl get nodes
# Deve mostrar 3 nós: minikube, minikube-m02, minikube-m03
```

### 3. Deploy da Aplicação

```bash
# Configurar Docker
eval $(minikube docker-env)

# Build das imagens
docker build -t modulo-a:v1 ./module-a
docker build -t modulo-b:v1 ./module-b
docker build -t modulo-p:v1 ./module-p

# Deploy completo (deployments + services)
kubectl apply -f k8s/deployment-modulo-a.yaml
kubectl apply -f k8s/deployment-modulo-b.yaml
kubectl apply -f k8s/deployment-modulo-p.yaml
kubectl apply -f k8s/service-modulo-a.yaml
kubectl apply -f k8s/service-modulo-b.yaml
kubectl apply -f k8s/service-modulo-p.yaml

# Aguardar
kubectl wait --for=condition=ready pod --all --timeout=120s

# Verificar
kubectl get pods
kubectl get services
```

### 4. Configurar HPA

```bash
# Aplicar HPAs
kubectl apply -f k8s/hpa-modulo-a.yaml
kubectl apply -f k8s/hpa-modulo-b.yaml
kubectl apply -f k8s/hpa-modulo-p.yaml

# Verificar
kubectl get hpa

# Deve mostrar algo como:
# NAME                REFERENCE              TARGETS   MINPODS   MAXPODS   REPLICAS
# voos-service-hpa    Deployment/voos-svc    15%/70%   2         10        2
# hoteis-service-hpa  Deployment/hoteis-svc  12%/70%   2         10        2
# api-gateway-hpa     Deployment/api-gateway 20%/70%   2         15        2
```

### 5. Deploy do Prometheus

```bash
# Namespace
kubectl apply -f k8s/prometheus-namespace.yaml

# RBAC
kubectl apply -f k8s/prometheus-rbac.yaml

# ConfigMap
kubectl apply -f k8s/prometheus-config.yaml

# Deployment e Service
kubectl apply -f k8s/prometheus-deployment.yaml
kubectl apply -f k8s/prometheus-service.yaml

# Aguardar
kubectl wait --for=condition=ready pod -n monitoring -l app=prometheus --timeout=120s

# Verificar
kubectl get all -n monitoring
```

### 6. Acessar Interfaces

```bash
# API Gateway (aplicação)
minikube service api-gateway --url
# Anotar URL: http://192.168.49.2:30000

# Prometheus
minikube service prometheus -n monitoring --url
# Anotar URL: http://192.168.49.2:30090

# Kubernetes Dashboard
minikube dashboard
```

### 7. Setup de Testes de Carga

```bash
cd load-tests

# Virtual environment
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Verificar
locust --version
```

### 8. Executar Testes

**Terminal 1 - Monitorar Pods**:
```bash
watch -n 2 kubectl get pods
```

**Terminal 2 - Monitorar HPA**:
```bash
watch -n 2 kubectl get hpa
```

**Terminal 3 - Executar Teste**:
```bash
cd load-tests
./run_tests.sh scenario cenario_1_baseline
```

**Browser 1 - Prometheus**:
- Abrir URL do Prometheus
- Executar queries (ver seção abaixo)

**Browser 2 - Dashboard**:
- Abrir Kubernetes Dashboard
- Monitorar recursos

### 9. Cenários de Teste a Executar

Execute pelo menos estes 5 cenários:

```bash
# 1. Baseline (sem HPA)
./run_tests.sh scenario cenario_1_baseline

# 2. HPA Moderado
./run_tests.sh scenario cenario_2_moderate

# 3. Alta Carga
./run_tests.sh scenario cenario_3_high_load

# 4. Teste de Estresse
./run_tests.sh scenario cenario_4_stress

# 5. Spike Test
./run_tests.sh scenario cenario_5_spike

# Aguardar 5 minutos entre cada cenário!
```

### 10. Coletar Resultados

Após cada teste:

```bash
# Métricas Kubernetes
kubectl top pods > results/cenarioX_metrics.txt
kubectl get hpa > results/cenarioX_hpa.txt

# Resultados Locust já salvos em results/
ls -lh results/
```

## Queries Prometheus Essenciais

Execute estas queries no Prometheus para cada cenário:

### Taxa de Requisições
```promql
sum(rate(http_requests_total[5m]))
```

### Latência P95
```promql
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```

### Uso de CPU
```promql
sum(rate(container_cpu_usage_seconds_total{namespace="default"}[5m])) by (pod)
```

### Uso de Memória
```promql
sum(container_memory_usage_bytes{namespace="default"}) by (pod) / 1024 / 1024
```

### Réplicas HPA
```promql
kube_deployment_status_replicas{deployment=~".*service|api-gateway"}
```

## Captura de Screenshots

Para o relatório, capturar:

1. **Kubernetes Dashboard**:
   - Visão geral do cluster (nós)
   - Lista de pods
   - Deployments
   - HPA em ação

2. **Prometheus**:
   - Query de taxa de requisições (gráfico)
   - Query de latência P95 (gráfico)
   - Query de uso de CPU (gráfico)
   - Targets (mostrando pods descobertos)

3. **Locust**:
   - Tela de configuração
   - Gráficos durante teste
   - Tabela de estatísticas
   - Relatório HTML final

4. **Terminal**:
   - Output de `kubectl get nodes`
   - Output de `kubectl get pods`
   - Output de `kubectl get hpa` durante teste
   - Output de `kubectl top pods`

## Checklist Pré-Entrega

Antes de entregar, verificar:

- [ ] Cluster com 3 nós funcionando
- [ ] Todos os pods em estado Running/Ready
- [ ] HPA configurado e funcionando
- [ ] Prometheus coletando métricas
- [ ] Mínimo 5 cenários de teste executados
- [ ] Resultados de cada cenário salvos em `load-tests/results/`
- [ ] Screenshots capturados
- [ ] Relatório preenchido (docs/RELATORIO_FINAL.md)
- [ ] Vídeo gravado mostrando o sistema funcionando
- [ ] Todos os arquivos de configuração incluídos
- [ ] GitHub atualizado (se aplicável)

## Estrutura de Entrega

Arquivo ZIP deve conter:

```
trabalho-pspd.zip
├── README.md
├── docs/
│   ├── RELATORIO_FINAL.md          ← PRINCIPAL
│   ├── KUBERNETES_SETUP.md
│   ├── PROMETHEUS_SETUP.md
│   └── screenshots/                 ← Screenshots
├── k8s/                             ← Todos os YAMLs
├── load-tests/
│   ├── results/                     ← Resultados dos testes
│   ├── locustfile.py
│   ├── scenarios.py
│   └── run_tests.sh
├── module-a/                        ← Código-fonte
├── module-b/
├── module-p/
└── video-apresentacao.mp4           ← Vídeo (ou link)
```

## Comandos de Troubleshooting

### Pods não iniciam

```bash
kubectl describe pod <pod-name>
kubectl logs <pod-name>
kubectl get events --sort-by=.metadata.creationTimestamp
```

### HPA não escala

```bash
# Verificar metrics-server
kubectl get deployment metrics-server -n kube-system

# Verificar métricas disponíveis
kubectl top pods

# Ver detalhes do HPA
kubectl describe hpa <hpa-name>
```

### Prometheus não coleta métricas

```bash
# Verificar se Prometheus está rodando
kubectl get pods -n monitoring

# Ver logs
kubectl logs -n monitoring <prometheus-pod>

# Verificar targets no Prometheus UI
# Status > Targets
```

### Locust não conecta

```bash
# Verificar se service está exposto
kubectl get svc api-gateway

# Testar conectividade
curl http://$(minikube ip):30000/health

# Verificar IP do Minikube
minikube ip
```

## Tempo Estimado

- Setup inicial: 30-60 min
- Execução de 5 cenários: 2-3 horas
- Análise de resultados: 1-2 horas
- Escrita do relatório: 3-4 horas
- Gravação do vídeo: 1-2 horas

**Total**: 8-12 horas de trabalho

## Dicas Finais

1. **Não pule a estabilização**: Aguarde 60s entre testes
2. **Monitore em tempo real**: Use watch e keep browsers abertos
3. **Documente durante**: Anote observações durante os testes
4. **Backup dos resultados**: Copie results/ frequentemente
5. **Screenshots durante**: Capture telas durante os testes, não depois
6. **Git commits**: Commite frequentemente
7. **Teste o vídeo**: Grave um teste antes da versão final

## Contatos em Caso de Problemas

- Documentação Kubernetes: https://kubernetes.io/docs/
- Documentação Prometheus: https://prometheus.io/docs/
- Documentação Locust: https://docs.locust.io/
- GitHub do Projeto: [seu-link]

---

**Boa sorte com o trabalho!**
