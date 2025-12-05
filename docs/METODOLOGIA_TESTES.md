# Metodologia de Testes e Cenários

## Visão Geral

Este documento descreve a metodologia completa para execução dos testes de carga, análise de desempenho e observabilidade do Sistema de Reservas de Voos.

## Metodologia de Testes

### 1. Configuração Base (Cenário Inicial)

**Objetivo**: Estabelecer baseline de performance

**Configuração Kubernetes**:
```yaml
Voos Service:
  replicas: 2
  resources:
    cpu: 100m-200m
    memory: 128Mi-256Mi
  hpa: disabled

Hotéis Service:
  replicas: 2
  resources:
    cpu: 100m-200m
    memory: 128Mi-256Mi
  hpa: disabled

API Gateway:
  replicas: 2
  resources:
    cpu: 100m-500m
    memory: 128Mi-512Mi
  hpa: disabled
```

**Teste de Carga**:
- Usuários simultâneos: 10
- Taxa de spawn: 2 usuários/segundo
- Duração: 5 minutos
- Ferramenta: Locust

**Métricas a Coletar**:
1. Tempo médio de resposta
2. Percentil 95 (P95) de latência
3. Percentil 99 (P99) de latência
4. Taxa de requisições por segundo (RPS)
5. Taxa de erro (%)
6. Uso de CPU por pod
7. Uso de memória por pod

**Como Executar**:
```bash
# 1. Configurar cluster
kubectl scale deployment voos-service --replicas=2
kubectl scale deployment hoteis-service --replicas=2
kubectl scale deployment api-gateway --replicas=2
kubectl delete hpa --all

# 2. Aguardar estabilização
sleep 30

# 3. Executar teste
cd load-tests
./run_tests.sh scenario cenario_1_baseline

# 4. Coletar métricas Kubernetes
kubectl top pods > results/cenario_1_k8s_metrics.txt

# 5. Coletar métricas Prometheus
# (acessar http://MINIKUBE_IP:30090 e executar queries)
```

**Resultados Esperados**:
- Latência P95: < 300ms
- Taxa de erro: 0%
- RPS: 40-60 requisições/segundo
- CPU: < 50% utilização
- Memória: Estável, sem crescimento

---

### 2. Variação de Cenários

Para cada cenário de teste, variar:

#### A. Quantidade de Réplicas

**Cenário 2a - Replicas Mínimas**:
- Todas as replicas = 1
- Objetivo: Identificar gargalos com recursos mínimos

**Cenário 2b - Replicas Balanceadas**:
- Voos: 3, Hotéis: 3, Gateway: 4
- Objetivo: Distribuição equilibrada

**Cenário 2c - Replicas Desbalanceadas**:
- Voos: 5, Hotéis: 2, Gateway: 3
- Objetivo: Testar impacto de desbalanceamento

#### B. Autoscaling (HPA)

**Cenário 3a - HPA Conservador**:
```yaml
minReplicas: 2
maxReplicas: 5
targetCPU: 80%
```

**Cenário 3b - HPA Agressivo**:
```yaml
minReplicas: 2
maxReplicas: 15
targetCPU: 60%
scaleUp: rápido (15s)
scaleDown: lento (300s)
```

**Cenário 3c - HPA Muito Agressivo**:
```yaml
minReplicas: 1
maxReplicas: 20
targetCPU: 50%
```

#### C. Carga de Trabalho

**Cenário 4a - Carga Crescente**:
```
0-5min:   50 usuários
5-10min:  100 usuários
10-15min: 200 usuários
15-20min: 300 usuários
```

**Cenário 4b - Spike Test**:
```
0-2min:  10 usuários
2-3min:  500 usuários (spike súbito!)
3-8min:  500 usuários sustentado
8-10min: 10 usuários (cool down)
```

**Cenário 4c - Carga Sustentada**:
```
Usuários: 150 constante
Duração: 30 minutos
Objetivo: Verificar estabilidade
```

#### D. Recursos (Limits/Requests)

**Cenário 5a - Recursos Generosos**:
```yaml
requests:
  cpu: 500m
  memory: 512Mi
limits:
  cpu: 2000m
  memory: 2Gi
```

**Cenário 5b - Recursos Restritos**:
```yaml
requests:
  cpu: 50m
  memory: 64Mi
limits:
  cpu: 100m
  memory: 128Mi
```

**Cenário 5c - Sem Limits** (não recomendado produção):
```yaml
requests:
  cpu: 100m
  memory: 128Mi
# Sem limits definidos
```

---

### 3. Protocolo de Execução de Cada Cenário

Para **cada cenário**, seguir este protocolo:

#### Passo 1: Preparação
```bash
# 1. Documentar configuração
echo "Cenário X: [descrição]" > results/cenarioX_config.txt
kubectl get deployments -o yaml >> results/cenarioX_config.txt
kubectl get hpa -o yaml >> results/cenarioX_config.txt

# 2. Aplicar configurações
kubectl apply -f k8s/cenarioX/

# 3. Aguardar estabilização (IMPORTANTE!)
sleep 60
kubectl wait --for=condition=ready pod --all --timeout=120s

# 4. Limpar métricas anteriores (restart Prometheus se necessário)
```

#### Passo 2: Coleta Baseline (Antes do Teste)
```bash
# Snapshot inicial
kubectl top nodes > results/cenarioX_nodes_before.txt
kubectl top pods > results/cenarioX_pods_before.txt
kubectl get pods -o wide > results/cenarioX_pods_distribution.txt
kubectl get hpa > results/cenarioX_hpa_before.txt
```

#### Passo 3: Execução do Teste
```bash
# Iniciar monitoramento contínuo (em terminal separado)
watch -n 10 'kubectl top pods >> results/cenarioX_pods_continuous.log'
watch -n 10 'kubectl get hpa >> results/cenarioX_hpa_continuous.log'

# Executar teste de carga
./run_tests.sh scenario cenarioX

# Ou manualmente:
locust -f locustfile.py \
  --host=http://$(minikube ip):30000 \
  --headless \
  --users=<N> \
  --spawn-rate=<R> \
  --run-time=<T> \
  --html=results/cenarioX_report.html \
  --csv=results/cenarioX
```

#### Passo 4: Monitoramento Durante Teste

**Terminal 1 - Pods**:
```bash
watch -n 2 kubectl get pods
```

**Terminal 2 - HPA**:
```bash
watch -n 2 kubectl get hpa
```

**Terminal 3 - Métricas**:
```bash
watch -n 5 kubectl top pods
```

**Browser 1 - Prometheus**:
- Abrir: http://MINIKUBE_IP:30090
- Executar queries relevantes (ver seção Queries)

**Browser 2 - Locust** (se não headless):
- Abrir: http://localhost:8089
- Monitorar gráficos em tempo real

**Browser 3 - Kubernetes Dashboard**:
```bash
minikube dashboard
```

#### Passo 5: Coleta Pós-Teste
```bash
# Snapshot final
kubectl top nodes > results/cenarioX_nodes_after.txt
kubectl top pods > results/cenarioX_pods_after.txt
kubectl get hpa > results/cenarioX_hpa_after.txt
kubectl get events --sort-by=.metadata.creationTimestamp > results/cenarioX_events.txt

# Logs (se houver erros)
kubectl logs -l app=voos-service --tail=100 > results/cenarioX_voos_logs.txt
kubectl logs -l app=hoteis-service --tail=100 > results/cenarioX_hoteis_logs.txt
kubectl logs -l app=api-gateway --tail=100 > results/cenarioX_gateway_logs.txt
```

#### Passo 6: Captura de Métricas Prometheus

Executar queries e salvar resultados:

```promql
# 1. Taxa de requisições
rate(http_requests_total[5m])

# 2. Latência P95
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# 3. Taxa de erro
sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m])) * 100

# 4. CPU por pod
rate(container_cpu_usage_seconds_total{namespace="default"}[5m])

# 5. Memória por pod
container_memory_usage_bytes{namespace="default"}

# 6. Número de réplicas ao longo do tempo
kube_deployment_status_replicas{deployment=~".*service|api-gateway"}
```

Exportar gráficos (screenshot ou CSV).

#### Passo 7: Análise Imediata

Responder perguntas:

1. **Desempenho**:
   - Latência ficou dentro do SLA (P95 < 500ms)?
   - Taxa de erro aceitável (< 1%)?
   - RPS alcançado vs esperado?

2. **Escalabilidade**:
   - HPA escalou adequadamente?
   - Quanto tempo para scale-up?
   - Scale-down ocorreu corretamente?

3. **Recursos**:
   - CPU/Memória dentro dos limits?
   - Houve throttling?
   - Recursos subutilizados ou saturados?

4. **Estabilidade**:
   - Pods reiniciaram?
   - Erros de OOMKilled?
   - Distribuição balanceada entre nodes?

#### Passo 8: Cool Down

```bash
# Aguardar sistema retornar ao normal
sleep 300  # 5 minutos

# Verificar se pods voltaram ao mínimo (se HPA ativo)
kubectl get hpa

# Preparar para próximo cenário
```

---

### 4. Queries Prometheus para Cada Cenário

#### Taxa de Requisições
```promql
# Total
sum(rate(http_requests_total[5m]))

# Por serviço
sum(rate(http_requests_total[5m])) by (job)

# Por endpoint
sum(rate(http_requests_total[5m])) by (endpoint)
```

#### Latência
```promql
# P50, P95, P99
histogram_quantile(0.50, rate(http_request_duration_seconds_bucket[5m]))
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))

# Por endpoint
histogram_quantile(0.95,
  sum(rate(http_request_duration_seconds_bucket[5m])) by (le, endpoint)
)
```

#### Recursos
```promql
# CPU por pod
sum(rate(container_cpu_usage_seconds_total{namespace="default"}[5m])) by (pod)

# Memória por pod
sum(container_memory_usage_bytes{namespace="default"}) by (pod)

# CPU % (relativo ao request)
sum(rate(container_cpu_usage_seconds_total{namespace="default"}[5m])) by (pod)
/
sum(kube_pod_container_resource_requests{resource="cpu"}) by (pod)
* 100
```

#### HPA
```promql
# Réplicas atuais
kube_deployment_status_replicas{deployment=~".*service|api-gateway"}

# Réplicas desejadas
kube_deployment_spec_replicas{deployment=~".*service|api-gateway"}

# Comparação
kube_deployment_status_replicas{deployment="voos-service"}
vs
kube_deployment_spec_replicas{deployment="voos-service"}
```

---

### 5. Template de Documentação de Resultados

Para cada cenário, documentar:

```markdown
## Cenário X: [Nome Descritivo]

### Configuração

**Kubernetes**:
- Voos Service: X réplicas, CPU/Mem
- Hotéis Service: X réplicas, CPU/Mem
- API Gateway: X réplicas, CPU/Mem
- HPA: Habilitado/Desabilitado (min/max)

**Teste de Carga**:
- Usuários: X
- Spawn rate: X/s
- Duração: X minutos
- Padrão: Constante/Crescente/Spike

### Objetivo

[Descrever o que se quer avaliar neste cenário]

### Hipótese

[O que se espera observar]

### Resultados

**Métricas Locust**:
| Métrica | Valor |
|---------|-------|
| RPS médio | X |
| RPS máximo | X |
| Latência média | X ms |
| Latência P95 | X ms |
| Latência P99 | X ms |
| Taxa de erro | X% |
| Total requisições | X |

**Recursos Kubernetes**:
| Pod | CPU Inicial | CPU Máximo | Mem Inicial | Mem Máximo |
|-----|-------------|------------|-------------|------------|
| voos-xxx | X | X | X | X |
| hoteis-xxx | X | X | X | X |
| api-gateway-xxx | X | X | X | X |

**HPA (se aplicável)**:
- Tempo até primeiro scale-up: X segundos
- Réplicas máximas alcançadas: X
- Tempo de scale-down: X segundos

**Gráficos**:
[Inserir screenshots de Prometheus, Locust, etc.]

### Observações

[Comportamentos notados durante o teste]

### Problemas Encontrados

[Erros, gargalos, comportamentos inesperados]

### Análise

[Interpretação dos resultados]

### Conclusão

[Responder: objetivo foi alcançado? Hipótese confirmada?]

### Próximos Passos

[O que testar em seguida baseado nestes resultados]
```

---

### 6. Comparação Entre Cenários

Após executar múltiplos cenários, criar tabela comparativa:

| Cenário | Config | Usuários | RPS | P95 Latência | Erro% | CPU Máx | Réplicas Máx | Observações |
|---------|--------|----------|-----|--------------|-------|---------|--------------|-------------|
| 1 - Baseline | 2/2/2, sem HPA | 10 | 45 | 180ms | 0% | 150m | 2 | Estável |
| 2 - HPA Mod | 2/2/2, HPA max 10 | 50 | 180 | 350ms | 0.2% | 180m | 5 | HPA funcionou bem |
| 3 - Alta Carga | 3/3/3, HPA max 15 | 200 | 520 | 680ms | 1.5% | 200m | 12 | Próximo do limite |
| 4 - Stress | 2/2/2, HPA max 20 | 500 | 650 | 2100ms | 8% | 200m | 15 | Sistema saturado |
| ... | ... | ... | ... | ... | ... | ... | ... | ... |

**Gráficos Comparativos**:
- Latência P95 vs Carga (usuários)
- RPS vs Número de réplicas
- Custo (réplicas) vs Performance (latência)

---

### 7. Garantir Mesmas Condições

Para evitar contaminação entre testes:

1. **Limpar estado**:
```bash
kubectl delete pods --all
kubectl wait --for=condition=ready pod --all
```

2. **Reiniciar Prometheus** (se necessário):
```bash
kubectl rollout restart deployment prometheus -n monitoring
```

3. **Aguardar estabilização**: Sempre 60s+ antes de iniciar teste

4. **Verificar recursos do host**:
```bash
# Linux
free -h
top

# macOS
vm_stat
top

# Garantir que host não está sob carga
```

5. **Minikube limpo**:
```bash
# Se necessário, reiniciar Minikube
minikube stop
minikube start
```

6. **Horário consistente**: Executar testes no mesmo horário (evitar variações de rede)

---

### 8. Checklist Pré-Teste

Antes de **cada** teste, verificar:

- [ ] Cluster Kubernetes rodando (`kubectl get nodes`)
- [ ] Todos os pods em Ready (`kubectl get pods`)
- [ ] Prometheus coletando métricas (acessar UI)
- [ ] Metrics Server habilitado (`kubectl top nodes`)
- [ ] Ambiente Locust configurado (`locust --version`)
- [ ] Diretório results/ criado
- [ ] Configuração do cenário aplicada
- [ ] 60s+ de estabilização aguardados
- [ ] Terminais de monitoramento abertos
- [ ] Browsers de monitoramento abertos (Prometheus, Dashboard)

---

### 9. Troubleshooting Durante Testes

**Problema: Pods crashando**
```bash
# Ver logs
kubectl logs <pod-name> --previous

# Verificar eventos
kubectl get events --sort-by=.metadata.creationTimestamp

# Possíveis causas:
# - OOMKilled (memória insuficiente)
# - Liveness probe falhando
# - Erro na aplicação
```

**Problema: HPA não escala**
```bash
# Verificar métricas disponíveis
kubectl top pods

# Descrever HPA
kubectl describe hpa <hpa-name>

# Verificar se CPU excedeu threshold
# (pode estar abaixo do target)
```

**Problema: Locust não conecta**
```bash
# Verificar service
kubectl get svc api-gateway

# Testar conectividade
curl http://$(minikube ip):30000/health

# Verificar firewall
```

**Problema: Resultados inconsistentes**
```bash
# Pode ser:
# 1. Cache (adicionar query params aleatórios)
# 2. Recursos do host variáveis (reiniciar Minikube)
# 3. Rede instável (repetir teste)
```

---

## Resumo da Metodologia

1. **Baseline**: Cenário mínimo para referência
2. **Variações Controladas**: Mudar 1 variável por vez
3. **Protocolo Rigoroso**: Mesmos passos para todos os cenários
4. **Coleta Completa**: Múltiplas fontes de métricas
5. **Análise Imediata**: Documentar enquanto fresco
6. **Comparação**: Tabelas e gráficos comparativos
7. **Conclusões**: Baseadas em dados, não intuição

**Resultado Final**: Conjunto de dados robusto para identificar configuração ótima do sistema.
