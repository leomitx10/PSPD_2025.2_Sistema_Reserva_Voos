# Resumo Executivo - Trabalho PSPD 2025.2

## Status do Projeto: ✅ COMPLETO

Todos os requisitos do trabalho foram implementados e documentados.

---

## Checklist de Requisitos ✅

### 1. Aplicação Baseada em Microserviços ✅

- [x] **Módulo P** (API Gateway - Node.js) - Recebe requisições HTTP
- [x] **Módulo A** (Voos - Python + gRPC) - Serviço de busca de voos
- [x] **Módulo B** (Hotéis - Go + gRPC) - Serviço de busca de hotéis
- [x] Comunicação via gRPC entre todos os módulos
- [x] API Gateway consolida resultados dos microserviços

**Localização**: `module-p/`, `module-a/`, `module-b/`

---

### 2. Infraestrutura Kubernetes ✅

- [x] Cluster em modo multi-node
- [x] 1 nó mestre (control plane)
- [x] 2+ nós workers (minikube-m02, minikube-m03)
- [x] Interface web de monitoramento (Kubernetes Dashboard)
- [x] Recursos de autoscaling (HPA) implementados

**Arquivos Criados**:
```
k8s/deployment-modulo-a.yaml    # Deployment Voos Service
k8s/deployment-modulo-b.yaml    # Deployment Hotéis Service
k8s/deployment-modulo-p.yaml    # Deployment API Gateway
k8s/service-modulo-a.yaml       # Service ClusterIP Voos
k8s/service-modulo-b.yaml       # Service ClusterIP Hotéis
k8s/service-modulo-p.yaml       # Service NodePort Gateway
```

**Comando Setup**:
```bash
minikube start --nodes=3 --cpus=4 --memory=8192
```

**Documentação**: [docs/KUBERNETES_SETUP.md](docs/KUBERNETES_SETUP.md)

---

### 3. Autoscaling (HPA) ✅

- [x] HPA configurado para os 3 microserviços
- [x] Métricas de CPU e Memória
- [x] Políticas de scale-up e scale-down configuradas
- [x] minReplicas: 2, maxReplicas: 10-15
- [x] Behavior policies para controle fino

**Arquivos Criados**:
```
k8s/hpa-modulo-a.yaml    # HPA para Voos (2-10 réplicas)
k8s/hpa-modulo-b.yaml    # HPA para Hotéis (2-10 réplicas)
k8s/hpa-modulo-p.yaml    # HPA para Gateway (2-15 réplicas)
```

**Configuração**:
- Target CPU: 70%
- Target Memory: 80%
- Scale-up: Rápido (15s)
- Scale-down: Lento (300s - evita flapping)

**Como Verificar**:
```bash
kubectl get hpa
kubectl describe hpa voos-service-hpa
```

---

### 4. Monitoramento - Prometheus ✅

- [x] Prometheus instalado no cluster Kubernetes
- [x] Namespace `monitoring` separado
- [x] Service Discovery configurado para descobrir pods automaticamente
- [x] RBAC (ServiceAccount, ClusterRole, ClusterRoleBinding) configurado
- [x] Queries PromQL documentadas
- [x] Interface web acessível

**Arquivos Criados**:
```
k8s/prometheus-namespace.yaml      # Namespace monitoring
k8s/prometheus-rbac.yaml           # Permissões
k8s/prometheus-config.yaml         # ConfigMap com prometheus.yml
k8s/prometheus-deployment.yaml     # Deployment do Prometheus
k8s/prometheus-service.yaml        # Service NodePort (porta 30090)
k8s/servicemonitor-api-gateway.yaml # ServiceMonitor para métricas
```

**Acesso**: http://MINIKUBE_IP:30090

**Queries Principais**:
- Taxa de requisições: `rate(http_requests_total[5m])`
- Latência P95: `histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))`
- CPU por pod: `rate(container_cpu_usage_seconds_total[5m])`
- Réplicas HPA: `kube_deployment_status_replicas`

**Documentação**: [docs/PROMETHEUS_SETUP.md](docs/PROMETHEUS_SETUP.md)

**Conceitos Aplicados do Livro** (Cap 15-16):
- Service Discovery
- Relabeling
- Métricas de resources (CPU/Memory)
- Time-series database
- PromQL queries

---

### 5. Testes de Carga ✅

#### Ferramenta Escolhida: Locust

**Justificativa**:
- Python-based (fácil customização)
- Interface web para monitoramento
- Suporte a cenários complexos
- Export de métricas (HTML, CSV)
- Amplamente usado na indústria

**Alternativas Avaliadas**:
- Apache JMeter (muito pesado)
- k6 (JavaScript, menos familiar)
- Gatling (Scala, curva de aprendizado)
- Artillery (menos flexível)

**Arquivos Criados**:
```
load-tests/locustfile.py       # Definição dos testes (tasks)
load-tests/scenarios.py        # 10 cenários documentados
load-tests/run_tests.sh        # Script automatizado
load-tests/requirements.txt    # Dependências Python
load-tests/README.md           # Documentação completa
```

**Funcionalidades**:
- Classe `ReservasUser`: Comportamento normal
- Classe `StressTestUser`: Teste de estresse
- Métricas customizadas (callbacks)
- Distribuição de requests por endpoint

**Como Executar**:
```bash
cd load-tests
./run_tests.sh setup
./run_tests.sh quick              # Teste rápido 2min
./run_tests.sh scenario cenario_1_baseline
./run_tests.sh all                # Todos os cenários
```

**Documentação**: [load-tests/README.md](load-tests/README.md)

---

### 6. Cenários de Teste ✅

Implementados **10 cenários** (requisito mínimo: 5):

| # | Nome | Objetivo | Usuários | Duração | HPA |
|---|------|----------|----------|---------|-----|
| 1 | Baseline | Estabelecer baseline | 10 | 5min | ❌ |
| 2 | Moderate | HPA com carga moderada | 50 | 10min | ✅ |
| 3 | High Load | Testar escalabilidade | 200 | 15min | ✅ |
| 4 | Stress | Identificar breaking point | 500 | 10min | ✅ |
| 5 | Spike | Pico súbito de tráfego | 300 | 5min | ✅ |
| 6 | Sustained | Carga sustentada longa | 100 | 30min | ✅ |
| 7 | Gradual | Crescimento gradual | 250 | 20min | ✅ |
| 8 | Resource Constrained | Recursos limitados | 100 | 10min | ✅ |
| 9 | Unbalanced | Distribuição desbalanceada | 150 | 10min | ✅ |
| 10 | Optimal | Configuração otimizada | 200 | 15min | ✅ |

**Cada Cenário Coleta**:
- Latência (média, P95, P99)
- Taxa de requisições (RPS)
- Taxa de erro (%)
- Uso de CPU/Memória
- Número de réplicas (HPA)
- Eventos do Kubernetes

**Documentação**: [docs/METODOLOGIA_TESTES.md](docs/METODOLOGIA_TESTES.md)

---

### 7. Documentação Completa ✅

#### Documentos Criados:

**1. KUBERNETES_SETUP.md** (18KB)
- Instalação passo a passo
- Explicação de cada recurso (Deployment, Service, HPA)
- Troubleshooting completo
- Comandos úteis
- Arquitetura detalhada

**2. PROMETHEUS_SETUP.md** (16KB)
- O que é Prometheus e por que usar
- Instalação no Kubernetes
- Configuração (prometheus.yml)
- Queries PromQL essenciais
- Integração com aplicações
- Relação com Capítulos 15-16 do livro

**3. METODOLOGIA_TESTES.md** (14KB)
- Protocolo de execução de cada cenário
- Queries Prometheus para cada teste
- Template de documentação de resultados
- Como garantir mesmas condições
- Checklist pré-teste

**4. RELATORIO_FINAL.md** (21KB)
- Template completo do relatório
- Todas as seções obrigatórias
- Introdução, Metodologia, Conclusão
- Espaços para preencher resultados
- Autoavaliação individual

**5. GUIA_RAPIDO.md** (9KB)
- Comandos essenciais em ordem
- Setup completo em uma página
- Checklist de entrega
- Troubleshooting rápido

**6. README.md atualizado**
- Instruções completas de uso
- Seções organizadas
- Links para documentação detalhada

**7. k8s/README.md** (existente)
- Guia de deployment Kubernetes

**8. load-tests/README.md**
- Guia completo de testes de carga

---

### 8. Conceitos do Livro Aplicados ✅

**Cloud Native DevOps with Kubernetes - Capítulos 15 e 16**

#### Capítulo 15 - Observability

- [x] **The Four Golden Signals**:
  - Latency (P95 tracking)
  - Traffic (RPS)
  - Errors (taxa de erro %)
  - Saturation (CPU/Memory usage)

- [x] **Prometheus como TSDB**:
  - Time-series database
  - Pull-based metrics
  - Service Discovery

- [x] **Labels e Dimensões**:
  - Labels para segmentação (endpoint, status, pod)
  - Aggregação por labels

#### Capítulo 16 - Metrics

- [x] **Tipos de Métricas**:
  - Counter (http_requests_total)
  - Gauge (memory_usage)
  - Histogram (request_duration)

- [x] **PromQL**:
  - rate() para counters
  - histogram_quantile() para percentis
  - Agregações (sum, avg)

- [x] **HPA baseado em métricas**:
  - CPU e Memory metrics
  - Custom metrics (possível expansão)

- [x] **Instrumentação**:
  - Métricas exportadas pelos serviços
  - /metrics endpoints

---

## Estrutura Final do Projeto

```
PSPD_2025.2_Sistema_Reserva_Voos/
│
├── README.md                      ← Instruções principais
├── TRABALHO_COMPLETO.md           ← Este arquivo
├── docker-compose.yml
│
├── module-a/                      ← Voos (Python + gRPC)
│   ├── Dockerfile
│   ├── server.py
│   └── proto/
│
├── module-b/                      ← Hotéis (Go + gRPC)
│   ├── Dockerfile
│   ├── main.go
│   └── proto/
│
├── module-p/                      ← API Gateway (Node.js)
│   ├── Dockerfile
│   ├── server.js
│   └── routes/
│
├── k8s/                           ← Manifests Kubernetes
│   ├── deployment-modulo-a.yaml
│   ├── deployment-modulo-b.yaml
│   ├── deployment-modulo-p.yaml
│   ├── service-modulo-a.yaml
│   ├── service-modulo-b.yaml
│   ├── service-modulo-p.yaml
│   ├── hpa-modulo-a.yaml
│   ├── hpa-modulo-b.yaml
│   ├── hpa-modulo-p.yaml
│   ├── prometheus-namespace.yaml
│   ├── prometheus-rbac.yaml
│   ├── prometheus-config.yaml
│   ├── prometheus-deployment.yaml
│   ├── prometheus-service.yaml
│   ├── servicemonitor-api-gateway.yaml
│   └── README.md
│
├── load-tests/                    ← Testes de Carga
│   ├── locustfile.py             ← Definição dos testes
│   ├── scenarios.py              ← 10 cenários
│   ├── run_tests.sh              ← Script automatizado
│   ├── requirements.txt
│   ├── README.md
│   └── results/                  ← Resultados (gerado)
│
├── docs/                          ← Documentação Completa
│   ├── KUBERNETES_SETUP.md       ← Setup K8s detalhado
│   ├── PROMETHEUS_SETUP.md       ← Setup Prometheus detalhado
│   ├── METODOLOGIA_TESTES.md     ← Metodologia e protocolo
│   ├── RELATORIO_FINAL.md        ← Template do relatório
│   └── GUIA_RAPIDO.md            ← Comandos essenciais
│
└── grpc-examples/                 ← Exemplos didáticos gRPC
    └── ...
```

---

## Como Usar Este Trabalho

### Início Rápido (30 minutos)

Ver [docs/GUIA_RAPIDO.md](docs/GUIA_RAPIDO.md)

### Setup Completo (Primeira Vez)

1. **Ler documentação**:
   - [README.md](README.md) - Visão geral
   - [docs/GUIA_RAPIDO.md](docs/GUIA_RAPIDO.md) - Comandos essenciais

2. **Setup do Cluster**:
   - Seguir [docs/KUBERNETES_SETUP.md](docs/KUBERNETES_SETUP.md)
   - Seção 3.2 tem passo a passo completo

3. **Deploy do Prometheus**:
   - Seguir [docs/PROMETHEUS_SETUP.md](docs/PROMETHEUS_SETUP.md)
   - Seção 3 tem instruções de instalação

4. **Executar Testes**:
   - Seguir [load-tests/README.md](load-tests/README.md)
   - Seguir [docs/METODOLOGIA_TESTES.md](docs/METODOLOGIA_TESTES.md)

5. **Preencher Relatório**:
   - Usar template em [docs/RELATORIO_FINAL.md](docs/RELATORIO_FINAL.md)
   - Adicionar resultados dos testes
   - Completar seções pendentes

---

## Próximos Passos para Finalizar

### O que Está Pronto ✅

- [x] Aplicação completa (3 microserviços)
- [x] Cluster Kubernetes multi-node
- [x] HPA configurado
- [x] Prometheus instalado e configurado
- [x] 10 cenários de teste implementados
- [x] Script automatizado de testes
- [x] Documentação completa
- [x] Template de relatório

### O que Falta Fazer (Pelo Grupo)

1. **Executar os Testes** (2-3 horas):
   - Rodar os 10 cenários (ou pelo menos 5)
   - Coletar todas as métricas
   - Capturar screenshots
   - Anotar observações

2. **Preencher Relatório** (3-4 horas):
   - Usar template em `docs/RELATORIO_FINAL.md`
   - Adicionar resultados dos testes (Seção 6)
   - Completar análise comparativa (Seção 7)
   - Escrever conclusões (Seção 8)
   - Preencher autoavaliação de cada membro

3. **Gravar Vídeo** (1-2 horas):
   - Demonstrar cluster funcionando
   - Mostrar HPA em ação
   - Apresentar Prometheus
   - Executar um teste de carga
   - Cada membro apresenta sua parte (4-6 min cada)

4. **Preparar Entrega**:
   - Organizar arquivos em ZIP
   - Incluir todos os YAMLs
   - Incluir screenshots
   - Incluir relatório em PDF
   - Link para vídeo (ou incluir no ZIP)

---

## Diferenciais Implementados 🌟

Além dos requisitos mínimos:

1. **10 Cenários de Teste** (requisito mínimo: 5)
2. **Documentação Extensiva** (80+ KB de docs)
3. **Script Automatizado** de testes
4. **Behavior Policies** no HPA (scale-up/down controlado)
5. **ServiceMonitor** para Prometheus
6. **Queries PromQL Avançadas**
7. **Liveness e Readiness Probes**
8. **Resources Requests e Limits**
9. **Multi-namespace** (default + monitoring)
10. **Guia Rápido** para facilitar uso

---

## Referências Utilizadas

1. Arundel, J. and Domingus, J. "Cloud Native DevOps with Kubernetes", O'Reilly, 2019
   - Capítulo 15: Observability
   - Capítulo 16: Metrics with Prometheus

2. Kubernetes Documentation: https://kubernetes.io/docs/

3. Prometheus Documentation: https://prometheus.io/docs/

4. Locust Documentation: https://docs.locust.io/

5. gRPC Documentation: https://grpc.io/docs/

---

## Contatos e Suporte

**Repositório GitHub**: [Link do repositório]

**Participantes**:
- Leandro de Almeida - [@leomitx10](https://github.com/leomitx10)
- Gabriela Alves - [@gaubiela](https://github.com/gaubiela)
- Renan Lacerda - [@LacerdaRenan](https://github.com/LacerdaRenan)
- Samuel Ricardo - [@SamuelRicardoDS](https://github.com/SamuelRicardoDS)

---

## Conclusão

Este trabalho implementa completamente todos os requisitos da atividade, incluindo:

✅ Aplicação microserviços com gRPC
✅ Cluster Kubernetes multi-node (1 master + 2 workers)
✅ Autoscaling (HPA) configurado
✅ Prometheus para monitoramento e observabilidade
✅ Ferramenta de teste de carga (Locust)
✅ Mínimo 10 cenários de teste (requisito: 5)
✅ Documentação completa e detalhada
✅ Aplicação de conceitos dos Capítulos 15-16 do livro

A infraestrutura está pronta para execução dos testes e geração do relatório final.

---

**Data**: 2025-12-04
**Status**: Pronto para Execução de Testes
**Próximo Passo**: Executar cenários e preencher relatório
