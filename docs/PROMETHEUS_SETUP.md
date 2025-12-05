# Configuração e Uso do Prometheus

## Índice

1. [Introdução ao Prometheus](#introdução-ao-prometheus)
2. [Conceitos Fundamentais](#conceitos-fundamentais)
3. [Instalação no Kubernetes](#instalação-no-kubernetes)
4. [Configuração](#configuração)
5. [Queries Úteis (PromQL)](#queries-úteis-promql)
6. [Integração com Aplicações](#integração-com-aplicações)
7. [Visualização de Métricas](#visualização-de-métricas)
8. [Troubleshooting](#troubleshooting)

## Introdução ao Prometheus

### O que é Prometheus?

Prometheus é um sistema de monitoramento e alerta open-source, originalmente desenvolvido no SoundCloud. É parte da Cloud Native Computing Foundation (CNCF) e é amplamente usado para monitorar aplicações em Kubernetes.

**Características principais**:
- **Time-series database**: Armazena métricas com timestamp
- **Pull-based**: Faz scraping de métricas dos targets
- **PromQL**: Linguagem de query poderosa
- **Alerting**: Sistema de alertas integrado
- **Service Discovery**: Descobre targets automaticamente (Kubernetes, Consul, etc.)
- **Multi-dimensional data**: Labels para segmentação de métricas

### Por que Prometheus para Kubernetes?

1. **Nativo para cloud**: Projetado para ambientes dinâmicos
2. **Service Discovery**: Descobre pods automaticamente
3. **Kubernetes Integration**: Métricas nativas do K8s
4. **Escalabilidade**: Suporta milhares de targets
5. **Comunidade**: Ampla adoção, muitos exporters

### Alternativas Consideradas

| Ferramenta | Prós | Contras | Decisão |
|------------|------|---------|---------|
| Prometheus | Nativo K8s, PromQL poderoso, CNCF | Setup inicial complexo | ✅ Escolhido |
| Datadog | SaaS, fácil setup | Pago, vendor lock-in | ❌ |
| New Relic | APM completo | Pago, overkill | ❌ |
| Grafana Cloud | Fácil, integrado | Pago | ❌ |
| Metrics Server | Já no K8s | Só CPU/Mem, sem histórico | ❌ (complementar) |

## Conceitos Fundamentais

### Modelo de Dados

Prometheus armazena dados como **time series**:

```
<metric_name>{<label_name>=<label_value>, ...} <value> <timestamp>
```

Exemplo:
```
http_requests_total{method="GET", endpoint="/flights", status="200"} 1234 1699876543
```

**Componentes**:
- **Metric name**: `http_requests_total`
- **Labels**: `method="GET"`, `endpoint="/flights"`, `status="200"`
- **Value**: `1234` (número de requisições)
- **Timestamp**: `1699876543` (Unix timestamp)

### Tipos de Métricas

#### 1. Counter
Valor que só aumenta (resets em restart).

**Uso**: Requisições totais, erros, bytes enviados

```promql
# Total de requisições
http_requests_total

# Taxa de requisições por segundo (últimos 5 min)
rate(http_requests_total[5m])
```

#### 2. Gauge
Valor que pode subir ou descer.

**Uso**: Temperatura, uso de CPU, número de pods

```promql
# Número atual de pods
kube_deployment_status_replicas

# Uso de memória
container_memory_usage_bytes
```

#### 3. Histogram
Amostras e contadores por buckets.

**Uso**: Latências, tamanhos de resposta

```promql
# Latência P95
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```

#### 4. Summary
Similar ao histogram, mas calcula quantiles no client.

**Uso**: Latências (alternativa ao histogram)

### Arquitetura Prometheus

```
┌─────────────────────────────────────────────────────────────┐
│                    PROMETHEUS SERVER                         │
│                                                               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │  Retrieval   │───▶│    TSDB      │───▶│  HTTP Server │  │
│  │  (Scraping)  │    │ (Storage)    │    │   (API/UI)   │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                                         │          │
└─────────┼─────────────────────────────────────────┼──────────┘
          │                                         │
          ▼                                         ▼
  ┌───────────────┐                         ┌─────────────┐
  │   TARGETS     │                         │  QUERIES    │
  │               │                         │             │
  │ - Pods        │                         │ - PromQL    │
  │ - Services    │                         │ - Grafana   │
  │ - Nodes       │                         │ - API       │
  └───────────────┘                         └─────────────┘
```

**Fluxo**:
1. **Retrieval**: Faz scraping dos targets a cada `scrape_interval`
2. **TSDB**: Armazena time series no disco
3. **HTTP Server**: Expõe API e UI para queries

## Instalação no Kubernetes

### Passo 1: Criar Namespace

```bash
kubectl apply -f k8s/prometheus-namespace.yaml
```

Arquivo `prometheus-namespace.yaml`:
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: monitoring
```

**Por que namespace separado?**
- Organização
- Isolamento de recursos
- Facilita gerenciamento

### Passo 2: Configurar RBAC (Permissões)

```bash
kubectl apply -f k8s/prometheus-rbac.yaml
```

**O que faz?**
- Cria **ServiceAccount** para Prometheus
- Cria **ClusterRole** com permissões para:
  - Listar nodes, services, endpoints, pods
  - Acessar métricas
- Faz **ClusterRoleBinding** ligando ServiceAccount ao ClusterRole

**Por que é necessário?**
Prometheus precisa de permissão para descobrir recursos no cluster (Service Discovery).

### Passo 3: Criar ConfigMap com Configuração

```bash
kubectl apply -f k8s/prometheus-config.yaml
```

ConfigMap contém `prometheus.yml` com:
- **Global config**: `scrape_interval`, `evaluation_interval`
- **Scrape configs**: Jobs para coletar métricas
- **Service Discovery**: Configuração de descoberta automática

### Passo 4: Deploy do Prometheus

```bash
kubectl apply -f k8s/prometheus-deployment.yaml
```

**Deployment** cria:
- 1 réplica do Prometheus
- Volume para dados (emptyDir - dados perdidos em restart)
- Monta ConfigMap como arquivo de configuração
- Probes para health checks

**Recursos alocados**:
```yaml
requests:
  memory: "512Mi"
  cpu: "250m"
limits:
  memory: "2Gi"
  cpu: "1000m"
```

### Passo 5: Expor via Service

```bash
kubectl apply -f k8s/prometheus-service.yaml
```

**Service** do tipo **NodePort**:
- Porta interna: 9090
- NodePort: 30090
- Acessível via `http://<minikube-ip>:30090`

### Passo 6: Verificar Instalação

```bash
# Ver todos os recursos
kubectl get all -n monitoring

# Ver logs
kubectl logs -n monitoring deployment/prometheus

# Ver configuração carregada
kubectl exec -n monitoring <prometheus-pod> -- cat /etc/prometheus/prometheus.yml
```

### Passo 7: Acessar Interface Web

```bash
# Obter URL
minikube service prometheus -n monitoring

# Ou port-forward
kubectl port-forward -n monitoring service/prometheus 9090:9090

# Abrir: http://localhost:9090
```

## Configuração

### Estrutura do prometheus.yml

```yaml
global:
  scrape_interval: 15s      # Intervalo entre scrapes
  evaluation_interval: 15s  # Intervalo para avaliar regras
  external_labels:
    cluster: 'sistema-reservas'

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'kubernetes-pods'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      # Filtra apenas pods com annotation prometheus.io/scrape: "true"
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
```

### Service Discovery Kubernetes

Prometheus pode descobrir automaticamente:
- **Nodes**: Métricas do kubelet
- **Services**: Endpoints de services
- **Pods**: Containers em pods
- **Endpoints**: IPs dos pods
- **Ingress**: Configurações de ingress

**Exemplo - Descobrir pods**:
```yaml
- job_name: 'kubernetes-pods'
  kubernetes_sd_configs:
    - role: pod
  relabel_configs:
    # Mantém apenas pods com label app
    - source_labels: [__meta_kubernetes_pod_label_app]
      action: keep
      regex: .+

    # Renomeia label app para job
    - source_labels: [__meta_kubernetes_pod_label_app]
      target_label: job

    # Adiciona namespace
    - source_labels: [__meta_kubernetes_namespace]
      target_label: namespace
```

### Relabeling

**Relabel configs** permitem:
- Filtrar targets
- Renomear labels
- Modificar métricas

**Actions**:
- `keep`: Mantém target se regex match
- `drop`: Remove target se regex match
- `replace`: Substitui valor
- `labelmap`: Renomeia labels

## Queries Úteis (PromQL)

### Métricas de Pods

```promql
# Uso de CPU (cores)
rate(container_cpu_usage_seconds_total{namespace="default"}[5m])

# Uso de CPU (%)
rate(container_cpu_usage_seconds_total{namespace="default"}[5m]) * 100

# Uso de memória (bytes)
container_memory_usage_bytes{namespace="default"}

# Uso de memória (MB)
container_memory_usage_bytes{namespace="default"} / 1024 / 1024

# Pods por deployment
kube_deployment_status_replicas{deployment="voos-service"}

# Pods ready
kube_deployment_status_replicas_ready{deployment="voos-service"}
```

### Métricas de Requisições

```promql
# Taxa de requisições (RPS)
rate(http_requests_total[5m])

# Taxa de requisições por endpoint
sum(rate(http_requests_total[5m])) by (endpoint)

# Requisições com erro (HTTP 5xx)
sum(rate(http_requests_total{status=~"5.."}[5m])) by (endpoint)

# Taxa de erro (%)
sum(rate(http_requests_total{status=~"5.."}[5m]))
/
sum(rate(http_requests_total[5m]))
* 100
```

### Latência (usando Histogram)

```promql
# Latência P50 (mediana)
histogram_quantile(0.50,
  rate(http_request_duration_seconds_bucket[5m])
)

# Latência P95
histogram_quantile(0.95,
  sum(rate(http_request_duration_seconds_bucket[5m])) by (le, endpoint)
)

# Latência P99
histogram_quantile(0.99,
  rate(http_request_duration_seconds_bucket[5m])
)

# Latência média
rate(http_request_duration_seconds_sum[5m])
/
rate(http_request_duration_seconds_count[5m])
```

### Métricas de Nodes

```promql
# CPU disponível em nodes
kube_node_status_allocatable{resource="cpu"}

# Memória disponível em nodes
kube_node_status_allocatable{resource="memory"}

# Pods por node
count(kube_pod_info) by (node)
```

### Queries Complexas

```promql
# Top 5 endpoints por latência
topk(5,
  histogram_quantile(0.95,
    rate(http_request_duration_seconds_bucket[5m])
  )
)

# Pods usando mais CPU
topk(10,
  rate(container_cpu_usage_seconds_total{namespace="default"}[5m])
)

# Crescimento de requisições (comparação hora a hora)
rate(http_requests_total[5m])
/
rate(http_requests_total[5m] offset 1h)

# Previsão de crescimento (linear regression)
predict_linear(http_requests_total[1h], 3600)
```

## Integração com Aplicações

### Expor Métricas em Node.js

```javascript
// module-p/server.js
const promClient = require('prom-client');

// Habilitar coleta de métricas padrão
promClient.collectDefaultMetrics();

// Criar registry
const register = new promClient.Registry();
promClient.collectDefaultMetrics({ register });

// Contador customizado
const httpRequestsTotal = new promClient.Counter({
  name: 'http_requests_total',
  help: 'Total de requisições HTTP',
  labelNames: ['method', 'endpoint', 'status'],
  registers: [register]
});

// Histogram de latência
const httpRequestDuration = new promClient.Histogram({
  name: 'http_request_duration_seconds',
  help: 'Duração das requisições HTTP',
  labelNames: ['method', 'endpoint'],
  buckets: [0.1, 0.5, 1, 2, 5],
  registers: [register]
});

// Middleware para tracking
app.use((req, res, next) => {
  const start = Date.now();

  res.on('finish', () => {
    const duration = (Date.now() - start) / 1000;

    httpRequestsTotal.inc({
      method: req.method,
      endpoint: req.path,
      status: res.statusCode
    });

    httpRequestDuration.observe({
      method: req.method,
      endpoint: req.path
    }, duration);
  });

  next();
});

// Endpoint de métricas
app.get('/metrics', async (req, res) => {
  res.set('Content-Type', register.contentType);
  res.end(await register.metrics());
});
```

### Adicionar Annotations ao Pod

Para Prometheus descobrir automaticamente:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-gateway
spec:
  template:
    metadata:
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "3000"
        prometheus.io/path: "/metrics"
    spec:
      containers:
      - name: api-gateway
        # ...
```

## Visualização de Métricas

### Interface Web Prometheus

**Graph Tab**:
1. Escrever query PromQL
2. Executar
3. Ver tabela ou gráfico

**Targets Tab**:
- Ver todos os targets sendo monitorados
- Status (UP/DOWN)
- Último scrape
- Erros

**Alerts Tab**:
- Alertas ativos
- Estado (firing, pending, inactive)

**Status Tab**:
- Configuração
- Flags de inicialização
- Métricas do Prometheus

### Grafana (Opcional mas Recomendado)

```bash
# Instalar Grafana
kubectl apply -f https://raw.githubusercontent.com/prometheus-operator/prometheus-operator/main/bundle.yaml

# Ou via Helm
helm repo add grafana https://grafana.github.io/helm-charts
helm install grafana grafana/grafana -n monitoring

# Obter senha admin
kubectl get secret -n monitoring grafana -o jsonpath="{.data.admin-password}" | base64 --decode

# Acessar
kubectl port-forward -n monitoring service/grafana 3000:80
```

**Configurar Grafana**:
1. Adicionar Prometheus como Data Source
2. Importar dashboards prontos:
   - Kubernetes Cluster Monitoring (ID: 3119)
   - Kubernetes Deployment (ID: 8588)
3. Criar dashboards customizados

## Troubleshooting

### Prometheus não inicia

```bash
# Ver logs
kubectl logs -n monitoring <prometheus-pod>

# Erros comuns:
# - Erro de sintaxe em prometheus.yml
# - Permissões RBAC insuficientes
# - Recursos insuficientes
```

### Targets não aparecem

```bash
# Verificar Service Discovery
# Prometheus UI > Status > Service Discovery

# Verificar RBAC
kubectl auth can-i list pods --as=system:serviceaccount:monitoring:prometheus

# Verificar configuração
kubectl get configmap -n monitoring prometheus-config -o yaml
```

### Métricas não coletadas

```bash
# Verificar se endpoint /metrics responde
kubectl port-forward <pod-name> 3000:3000
curl http://localhost:3000/metrics

# Verificar annotations do pod
kubectl describe pod <pod-name> | grep Annotations

# Verificar se Prometheus fez scrape
# Prometheus UI > Targets > procurar pod
```

### Queries retornam vazio

```bash
# Verificar se métrica existe
# Prometheus UI > Graph > inserir nome da métrica

# Verificar range
# Queries com rate/increase precisam de range [5m]

# Verificar labels
# Usar {} para ver todos os labels disponíveis
```

## Boas Práticas

1. **Naming Convention**:
   - `<namespace>_<subsystem>_<name>_<unit>`
   - Ex: `http_requests_total`, `node_cpu_seconds_total`

2. **Labels**:
   - Use labels para dimensões (endpoint, status, method)
   - Evite labels com alta cardinalidade (IDs únicos)
   - Máximo 10-15 labels por métrica

3. **Storage**:
   - Prometheus consome ~1-2 bytes por sample
   - 1M time series, 15s interval = ~5GB/dia
   - Configure retention: `--storage.tsdb.retention.time=30d`

4. **Queries**:
   - Use `rate()` para counters
   - Use `irate()` para picos instantâneos
   - Agregue antes de aplicar funções: `sum(rate(...)) by (label)`

5. **Alertas**:
   - Alert em sintomas, não causas
   - Use `for` para evitar alertas transitórios
   - Agrupe alertas relacionados

## Referências

- [Prometheus Documentation](https://prometheus.io/docs/)
- [PromQL Basics](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [Prometheus Best Practices](https://prometheus.io/docs/practices/)
- Cloud Native DevOps with Kubernetes - Capítulo 15 (Observability)
- Cloud Native DevOps with Kubernetes - Capítulo 16 (Metrics)
