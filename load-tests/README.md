# Testes de Carga - Sistema de Reservas

Documentação completa dos testes de carga usando Locust para avaliar performance, escalabilidade e observabilidade do sistema distribuído.

## Índice

- [Ferramentas Utilizadas](#ferramentas-utilizadas)
- [Instalação](#instalação)
- [Cenários de Teste](#cenários-de-teste)
- [Como Executar](#como-executar)
- [Interpretação dos Resultados](#interpretação-dos-resultados)
- [Integração com Prometheus](#integração-com-prometheus)

## Ferramentas Utilizadas

### Locust

**Por que Locust?**

1. **Python-based**: Fácil de customizar e integrar
2. **Distributed Load Testing**: Suporta execução distribuída
3. **Web UI**: Interface web para monitoramento em tempo real
4. **Scriptable**: Cenários complexos em Python
5. **Metrics**: Exporta métricas detalhadas (CSV, HTML)
6. **Open Source**: Gratuito e amplamente usado

**Alternativas Consideradas:**
- **Apache JMeter**: Mais complexo, interface gráfica pesada
- **k6**: Ótimo mas usa JavaScript
- **Gatling**: Scala-based, curva de aprendizado maior
- **Artillery**: Focado em APIs, menos flexível

**Decisão**: Locust por sua simplicidade, flexibilidade e boa documentação.

## Instalação

### Pré-requisitos

```bash
# Python 3.8+
python3 --version

# pip
pip3 --version

# Virtual environment (recomendado)
python3 -m venv venv
```

### Setup

```bash
# 1. Entrar no diretório
cd load-tests

# 2. Criar e ativar virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Verificar instalação
locust --version
```

## Cenários de Teste

### Cenário 1: Baseline (Configuração Mínima)

**Objetivo**: Estabelecer baseline de performance sem autoscaling

**Configuração Kubernetes**:
- Voos Service: 2 réplicas
- Hotéis Service: 2 réplicas
- API Gateway: 2 réplicas
- HPA: Desabilitado

**Configuração de Carga**:
- Usuários: 10
- Spawn Rate: 2 usuários/segundo
- Duração: 5 minutos

**Métricas Esperadas**:
- Tempo médio de resposta: < 200ms
- Taxa de erro: < 1%
- Requisições/segundo: ~50-100

**Comando**:
```bash
./run_tests.sh scenario cenario_1_baseline
```

---

### Cenário 2: Carga Moderada (HPA Habilitado)

**Objetivo**: Avaliar comportamento do HPA com carga moderada

**Configuração Kubernetes**:
- Replicas iniciais: 2 para cada serviço
- HPA: Habilitado (max 10 réplicas)
- CPU threshold: 70%
- Memory threshold: 80%

**Configuração de Carga**:
- Usuários: 50
- Spawn Rate: 5 usuários/segundo
- Duração: 10 minutos

**Observações Esperadas**:
- HPA deve escalar até 4-6 réplicas
- Tempo de resposta deve se manter estável
- Scale-up em ~2-3 minutos
- Scale-down após pico de carga

---

### Cenário 3: Alta Carga

**Objetivo**: Testar limites de escalabilidade horizontal

**Configuração Kubernetes**:
- Replicas iniciais: 3 para cada serviço
- HPA: Habilitado (max 15 réplicas)

**Configuração de Carga**:
- Usuários: 200
- Spawn Rate: 10 usuários/segundo
- Duração: 15 minutos

---

### Cenário 4: Teste de Estresse

**Objetivo**: Identificar breaking point do sistema

**Configuração de Carga**:
- Usuários: 500
- Spawn Rate: 25 usuários/segundo
- Duração: 10 minutos

**O que observar**:
- Em que ponto o sistema começa a degradar?
- Taxa de erro aumenta acima de X requisições/s?
- Tempo de resposta ultrapassa SLA?

---

### Cenário 5: Spike Test

**Objetivo**: Avaliar resposta a picos súbitos de tráfego

**Configuração de Carga**:
- Usuários: 300
- Spawn Rate: 100 usuários/segundo (muito rápido!)
- Duração: 5 minutos

**O que avaliar**:
- HPA reage rápido o suficiente?
- Sistema mantém estabilidade?
- Há queue/throttling?

---

### Cenário 6: Carga Sustentada

**Objetivo**: Verificar estabilidade com carga constante prolongada

**Configuração de Carga**:
- Usuários: 100
- Spawn Rate: 5 usuários/segundo
- Duração: 30 minutos

**O que monitorar**:
- Memory leaks?
- Degradação de performance ao longo do tempo?
- Estabilidade das réplicas?

---

### Cenário 7-10

Veja arquivo `scenarios.py` para detalhes completos dos demais cenários.

## Como Executar

### Teste Rápido (Recomendado para começar)

```bash
# Configurar ambiente
./run_tests.sh setup

# Teste rápido (2 min, 50 usuários)
./run_tests.sh quick
```

### Cenário Específico

```bash
./run_tests.sh scenario cenario_1_baseline
./run_tests.sh scenario cenario_2_moderate
./run_tests.sh scenario cenario_3_high_load
```

### Todos os Cenários (Teste Completo)

```bash
# Executa cenários 1, 2 e 3 sequencialmente
./run_tests.sh all

# ATENÇÃO: Pode levar 30+ minutos
```

### Modo Manual (Locust Web UI)

```bash
# 1. Obter IP do Minikube
export MINIKUBE_IP=$(minikube ip)

# 2. Iniciar Locust com interface web
locust -f locustfile.py --host=http://${MINIKUBE_IP}:30000

# 3. Abrir navegador em http://localhost:8089
# 4. Configurar número de usuários e spawn rate
# 5. Iniciar teste e monitorar em tempo real
```

### Modo Headless (Automatizado)

```bash
locust -f locustfile.py \
    --host=http://$(minikube ip):30000 \
    --headless \
    --users=100 \
    --spawn-rate=10 \
    --run-time=5m \
    --html=results/custom_test_report.html \
    --csv=results/custom_test
```

## Interpretação dos Resultados

### Arquivos Gerados

Após execução, encontrará em `results/`:

```
results/
├── cenario_1_baseline_report.html       # Relatório visual completo
├── cenario_1_baseline_stats.csv         # Estatísticas agregadas
├── cenario_1_baseline_failures.csv      # Falhas registradas
├── cenario_1_baseline_stats_history.csv # Histórico temporal
├── cenario_1_baseline_k8s_metrics.txt   # Métricas do Kubernetes
└── cenario_1_baseline_hpa_status.txt    # Status do HPA
```

### Métricas Principais

**1. Response Time (Tempo de Resposta)**
```
Tipo         Requisições  Falhas  Mediana  95%ile  99%ile  Avg
GET /flights   10000      0       150ms    280ms   450ms   180ms
```

- **Mediana**: 50% das requisições abaixo deste valor
- **95%ile**: 95% das requisições abaixo deste valor (SLA típico)
- **99%ile**: Pior caso (outliers)
- **Avg**: Média (pode ser distorcida por outliers)

**Meta**: 95%ile < 500ms

**2. Throughput (Requisições/segundo)**
```
RPS (requests/second): 250
```

**Meta**: Sistema deve suportar picos de 200+ RPS

**3. Taxa de Erro**
```
Failure Rate: 0.5% (50 de 10000)
```

**Meta**: < 1% de erros

**4. Uso de Recursos (Kubernetes)**
```
NAME                    CPU    MEMORY
api-gateway-xxx         450m   320Mi
voos-service-xxx        280m   180Mi
hoteis-service-xxx      250m   160Mi
```

**Avaliar**:
- CPU próximo do limit? Considere aumentar
- Memory creep? Possível leak
- Discrepância entre pods? Load balancing ok?

### Análise Comparativa

**Exemplo de Comparação**:

| Cenário | Usuários | RPS | Tempo Médio | P95 | Taxa Erro | Réplicas Máx |
|---------|----------|-----|-------------|-----|-----------|--------------|
| 1 - Baseline | 10 | 45 | 120ms | 180ms | 0% | 2 (fixo) |
| 2 - Moderate | 50 | 180 | 210ms | 380ms | 0.2% | 5 |
| 3 - High Load | 200 | 520 | 350ms | 680ms | 1.8% | 12 |
| 4 - Stress | 500 | 650 | 1200ms | 2500ms | 8.5% | 15 |

**Observações**:
- Cenário 3: Melhor relação performance/recursos
- Cenário 4: Sistema atinge limite (>1% erro)
- **Configuração ótima**: ~8-10 réplicas para 200-300 RPS

## Integração com Prometheus

### Verificar Métricas no Prometheus

```bash
# 1. Acessar Prometheus
minikube service prometheus -n monitoring

# 2. Queries úteis (no Prometheus UI):

# Taxa de requisições
rate(http_requests_total[5m])

# Latência (percentil 95)
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Uso de CPU por pod
rate(container_cpu_usage_seconds_total[5m])

# Uso de memória
container_memory_usage_bytes

# Status do HPA
kube_hpa_status_current_replicas
```

### Durante os Testes

1. **Terminal 1**: Executar teste Locust
   ```bash
   ./run_tests.sh scenario cenario_2_moderate
   ```

2. **Terminal 2**: Monitorar pods
   ```bash
   watch -n 2 kubectl get pods
   ```

3. **Terminal 3**: Monitorar HPA
   ```bash
   watch -n 2 kubectl get hpa
   ```

4. **Browser 1**: Locust Web UI (http://localhost:8089)

5. **Browser 2**: Prometheus (http://MINIKUBE_IP:30090)

6. **Browser 3**: Kubernetes Dashboard
   ```bash
   minikube dashboard
   ```

## Troubleshooting

### Erro: Connection refused

```bash
# Verificar se aplicação está rodando
kubectl get pods
kubectl get svc

# Testar conectividade
curl http://$(minikube ip):30000/health
```

### Erro: Locust não encontrado

```bash
# Verificar virtual environment
source venv/bin/activate
which locust

# Reinstalar se necessário
pip install locust
```

### Testes muito lentos

1. Reduzir número de usuários
2. Reduzir duração
3. Verificar recursos do Minikube:
   ```bash
   minikube config set memory 4096
   minikube config set cpus 4
   minikube delete
   minikube start
   ```

### Resultados inconsistentes

1. Limpar estado entre testes:
   ```bash
   kubectl delete pods --all
   kubectl wait --for=condition=ready pod --all
   ```

2. Aguardar estabilização (30-60s)

3. Verificar recursos do host:
   ```bash
   top
   free -h
   ```

## Próximos Passos

1. **Executar todos os cenários**: `./run_tests.sh all`
2. **Analisar resultados**: Comparar métricas entre cenários
3. **Ajustar configurações**: Otimizar baseado em resultados
4. **Documentar**: Adicionar findings ao relatório final
5. **Validar**: Re-executar cenário otimizado

## Referências

- [Documentação Locust](https://docs.locust.io/)
- [Best Practices Load Testing](https://locust.io/best-practices)
- [Prometheus Query Examples](https://prometheus.io/docs/prometheus/latest/querying/examples/)
- Cloud Native DevOps with Kubernetes - Capítulos 15 e 16
