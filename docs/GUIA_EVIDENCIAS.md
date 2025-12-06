# Guia de Coleta de Evidências - Kubernetes

## 📋 Checklist de Evidências Necessárias

### 1. Cluster Kubernetes (Obrigatório)

#### 1.1 Informações dos Nós
```bash
# Listar nós do cluster (deve mostrar 1 master + 2+ workers)
kubectl get nodes -o wide

# Capturar screenshot ou salvar output
kubectl get nodes -o wide > evidencias/kubectl_nodes.txt
```

**O que verificar:**
- ✅ Mínimo 3 nós (1 master + 2 workers)
- ✅ Status "Ready" para todos
- ✅ Versão do Kubernetes

#### 1.2 Informações dos Pods
```bash
# Listar todos os pods
kubectl get pods --all-namespaces -o wide

# Pods da aplicação
kubectl get pods -n default

# Capturar
kubectl get pods -o wide > evidencias/kubectl_pods.txt
```

**O que verificar:**
- ✅ Pods P, A, B rodando
- ✅ Status "Running"
- ✅ Distribuição entre nós

#### 1.3 Deployments e ReplicaSets
```bash
# Listar deployments
kubectl get deployments

# Detalhes dos deployments
kubectl describe deployment module-p
kubectl describe deployment module-a
kubectl describe deployment module-b

# Capturar
kubectl get deployments -o yaml > evidencias/deployments.yaml
```

#### 1.4 Services
```bash
# Listar services
kubectl get services

# Detalhes
kubectl describe service module-p-service
kubectl describe service module-a-service
kubectl describe service module-b-service

# Capturar
kubectl get services -o wide > evidencias/services.txt
```

---

### 2. Horizontal Pod Autoscaler (HPA) - Obrigatório

#### 2.1 Status do HPA
```bash
# Listar HPAs
kubectl get hpa

# Detalhes
kubectl describe hpa module-a-hpa
kubectl describe hpa module-b-hpa
kubectl describe hpa module-p-hpa

# Capturar
kubectl get hpa > evidencias/hpa_status.txt
kubectl get hpa -o yaml > evidencias/hpa_config.yaml
```

**O que verificar:**
- ✅ HPA configurado para cada módulo
- ✅ Métricas de CPU/memória sendo coletadas
- ✅ Min/Max replicas configurados

#### 2.2 Teste de Autoscaling (CRUCIAL)
```bash
# Monitorar HPA em tempo real durante teste de carga
watch -n 2 "kubectl get hpa"

# EM OUTRO TERMINAL: executar teste de carga
cd load-tests
python3 execute_scenarios.py

# DURANTE O TESTE: capturar evidências
# Screenshot do watch mostrando HPA escalando
# Copiar outputs periodicamente
kubectl get hpa >> evidencias/hpa_durante_teste.log
kubectl get pods >> evidencias/pods_durante_teste.log
```

**Evidências necessárias:**
- ✅ Screenshot/log ANTES do teste (réplicas mínimas)
- ✅ Screenshot/log DURANTE o teste (réplicas aumentando)
- ✅ Screenshot/log DEPOIS do teste (réplicas diminuindo)

---

### 3. Métricas de Recursos

#### 3.1 Metrics Server (Necessário para HPA)
```bash
# Verificar se metrics-server está rodando
kubectl get deployment metrics-server -n kube-system

# Se não estiver, instalar:
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# Editar para permitir insecure TLS (ambiente de teste)
kubectl edit deployment metrics-server -n kube-system
# Adicionar: --kubelet-insecure-tls
```

#### 3.2 Uso de CPU e Memória
```bash
# Uso por nó
kubectl top nodes

# Uso por pod
kubectl top pods

# Capturar periodicamente durante testes
for i in {1..10}; do
  echo "=== Medição $i ===" >> evidencias/resource_usage.log
  kubectl top nodes >> evidencias/resource_usage.log
  kubectl top pods >> evidencias/resource_usage.log
  sleep 30
done
```

---

### 4. Prometheus (Obrigatório)

#### 4.1 Instalação e Status
```bash
# Verificar namespace do Prometheus
kubectl get all -n monitoring

# Verificar pods
kubectl get pods -n monitoring

# Capturar
kubectl get all -n monitoring > evidencias/prometheus_status.txt
```

#### 4.2 Acesso ao Prometheus
```bash
# Port-forward para acessar Prometheus UI
kubectl port-forward -n monitoring svc/prometheus-service 9090:9090

# Abrir no navegador: http://localhost:9090
```

**Screenshots necessários:**
1. ✅ Prometheus Targets (Status → Targets)
   - Mostrar que está coletando métricas da aplicação
   
2. ✅ Queries importantes:
   ```promql
   # Taxa de requisições
   rate(http_requests_total[5m])
   
   # Latência P95
   histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
   
   # Uso de CPU por pod
   container_cpu_usage_seconds_total{pod=~"module-.*"}
   
   # Uso de memória por pod
   container_memory_usage_bytes{pod=~"module-.*"}
   ```

3. ✅ Gráficos durante teste de carga
   - Screenshot mostrando aumento de métricas durante teste

---

### 5. Testes de Carga com Locust

#### 5.1 Executar Cenários
```bash
cd load-tests
python3 execute_scenarios.py
```

**Evidências:**
- ✅ Output do terminal mostrando execução
- ✅ Relatórios HTML gerados
- ✅ CSVs com estatísticas
- ✅ Screenshot de um relatório HTML aberto

#### 5.2 Análise de Resultados
```bash
# Gerar relatório comparativo
python3 analyze_results.py

# Capturar
python3 analyze_results.py > evidencias/analise_comparativa.txt
```

---

### 6. Logs da Aplicação

#### 6.1 Logs dos Pods
```bash
# Ver logs de cada módulo
kubectl logs deployment/module-p
kubectl logs deployment/module-a
kubectl logs deployment/module-b

# Logs durante teste
kubectl logs -f deployment/module-p > evidencias/logs_module_p.txt &
kubectl logs -f deployment/module-a > evidencias/logs_module_a.txt &
kubectl logs -f deployment/module-b > evidencias/logs_module_b.txt &

# Executar testes...

# Parar captura de logs
pkill -f "kubectl logs"
```

---

### 7. Configurações (para Anexo do Relatório)

#### 7.1 Exportar YAMLs
```bash
mkdir -p evidencias/manifests

# Deployments
kubectl get deployment module-p -o yaml > evidencias/manifests/deployment-p.yaml
kubectl get deployment module-a -o yaml > evidencias/manifests/deployment-a.yaml
kubectl get deployment module-b -o yaml > evidencias/manifests/deployment-b.yaml

# Services
kubectl get service module-p-service -o yaml > evidencias/manifests/service-p.yaml
kubectl get service module-a-service -o yaml > evidencias/manifests/service-a.yaml
kubectl get service module-b-service -o yaml > evidencias/manifests/service-b.yaml

# HPAs
kubectl get hpa -o yaml > evidencias/manifests/hpas.yaml

# Prometheus
kubectl get all -n monitoring -o yaml > evidencias/manifests/prometheus.yaml
```

---

## 🎯 Resumo de Evidências Obrigatórias

### Para o Relatório Final:

1. **Cluster K8s:**
   - [ ] Screenshot/print `kubectl get nodes` (3+ nós)
   - [ ] Screenshot/print `kubectl get pods`
   - [ ] Screenshot/print `kubectl get deployments`

2. **HPA em Ação:**
   - [ ] Screenshot HPA ANTES do teste (réplicas min)
   - [ ] Screenshot HPA DURANTE teste (escalando)
   - [ ] Screenshot HPA APÓS teste (descalando)
   - [ ] Logs mostrando eventos de scaling

3. **Prometheus:**
   - [ ] Screenshot Prometheus Targets (coleta ativa)
   - [ ] Screenshot query de throughput durante teste
   - [ ] Screenshot query de latência P95/P99
   - [ ] Screenshot uso CPU/memória por pod

4. **Testes de Carga:**
   - [ ] Screenshot relatório Locust (HTML)
   - [ ] Output do analyze_results.py
   - [ ] Tabela comparativa dos 5 cenários

5. **Métricas de Recursos:**
   - [ ] Output `kubectl top nodes` durante teste
   - [ ] Output `kubectl top pods` durante teste
   - [ ] Gráfico/tabela comparando uso antes/durante/depois

---

## 📊 Script Automatizado de Coleta

```bash
#!/bin/bash
# collect_evidences.sh

EVIDENCIAS_DIR="evidencias/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$EVIDENCIAS_DIR"

echo "📸 Coletando evidências do cluster..."

# Informações do cluster
kubectl get nodes -o wide > "$EVIDENCIAS_DIR/nodes.txt"
kubectl get pods --all-namespaces -o wide > "$EVIDENCIAS_DIR/all_pods.txt"
kubectl get deployments -o wide > "$EVIDENCIAS_DIR/deployments.txt"
kubectl get services -o wide > "$EVIDENCIAS_DIR/services.txt"
kubectl get hpa -o wide > "$EVIDENCIAS_DIR/hpa.txt"

# Recursos
kubectl top nodes > "$EVIDENCIAS_DIR/top_nodes.txt"
kubectl top pods > "$EVIDENCIAS_DIR/top_pods.txt"

# Prometheus
kubectl get all -n monitoring > "$EVIDENCIAS_DIR/prometheus.txt"

# Descrições detalhadas
for deploy in module-p module-a module-b; do
  kubectl describe deployment $deploy > "$EVIDENCIAS_DIR/describe_$deploy.txt"
  kubectl describe hpa ${deploy}-hpa > "$EVIDENCIAS_DIR/describe_hpa_$deploy.txt"
done

echo "✅ Evidências coletadas em: $EVIDENCIAS_DIR"
```

---

## 🚀 Passo a Passo para Coleta Completa

1. **Preparar ambiente:**
   ```bash
   mkdir -p evidencias
   chmod +x collect_evidences.sh
   ```

2. **Coletar estado inicial:**
   ```bash
   ./collect_evidences.sh
   ```

3. **Iniciar monitoramento em terminais separados:**
   ```bash
   # Terminal 1: HPA
   watch -n 2 "kubectl get hpa"
   
   # Terminal 2: Pods
   watch -n 2 "kubectl get pods"
   
   # Terminal 3: Recursos
   watch -n 5 "kubectl top pods"
   ```

4. **Executar testes:**
   ```bash
   # Terminal 4
   cd load-tests
   python3 execute_scenarios.py
   ```

5. **Durante os testes:**
   - Tirar screenshots dos terminais 1, 2, 3
   - Anotar momentos de scaling
   - Observar Prometheus (port-forward em outro terminal)

6. **Após os testes:**
   ```bash
   ./collect_evidences.sh
   python3 load-tests/analyze_results.py
   ```

7. **Organizar evidências:**
   - Nomear screenshots claramente
   - Criar documento com análises
   - Inserir no relatório final

---

**Fim do Guia**
