#!/bin/bash
# Script Automatizado de Coleta de Evidências
# Sistema de Reserva de Voos - PSPD 2025.2

set -e

EVIDENCIAS_DIR="evidencias/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$EVIDENCIAS_DIR"

echo "=================================="
echo "📸 Coleta de Evidências K8s"
echo "=================================="
echo ""
echo "Diretório: $EVIDENCIAS_DIR"
echo ""

# Verificar se kubectl está disponível
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl não encontrado. Instale o kubectl primeiro."
    exit 1
fi

echo "1️⃣  Coletando informações do cluster..."
kubectl cluster-info > "$EVIDENCIAS_DIR/cluster_info.txt" 2>&1 || echo "Erro ao coletar cluster-info"
kubectl get nodes -o wide > "$EVIDENCIAS_DIR/nodes.txt" 2>&1 || echo "Erro ao coletar nodes"
kubectl get nodes -o yaml > "$EVIDENCIAS_DIR/nodes.yaml" 2>&1 || echo "Erro ao coletar nodes YAML"

echo "2️⃣  Coletando informações de pods..."
kubectl get pods --all-namespaces -o wide > "$EVIDENCIAS_DIR/all_pods.txt" 2>&1 || echo "Erro ao coletar pods"
kubectl get pods -n default -o wide > "$EVIDENCIAS_DIR/default_pods.txt" 2>&1 || echo "Erro ao coletar default pods"
kubectl get pods -n default -o yaml > "$EVIDENCIAS_DIR/default_pods.yaml" 2>&1 || echo "Erro ao coletar pods YAML"

echo "3️⃣  Coletando deployments..."
kubectl get deployments -o wide > "$EVIDENCIAS_DIR/deployments.txt" 2>&1 || echo "Erro ao coletar deployments"
kubectl get deployments -o yaml > "$EVIDENCIAS_DIR/deployments.yaml" 2>&1 || echo "Erro ao coletar deployments YAML"

echo "4️⃣  Coletando services..."
kubectl get services -o wide > "$EVIDENCIAS_DIR/services.txt" 2>&1 || echo "Erro ao coletar services"
kubectl get services -o yaml > "$EVIDENCIAS_DIR/services.yaml" 2>&1 || echo "Erro ao coletar services YAML"

echo "5️⃣  Coletando HPA (Horizontal Pod Autoscaler)..."
kubectl get hpa -o wide > "$EVIDENCIAS_DIR/hpa.txt" 2>&1 || echo "Erro ao coletar HPA"
kubectl get hpa -o yaml > "$EVIDENCIAS_DIR/hpa.yaml" 2>&1 || echo "Erro ao coletar HPA YAML"

echo "6️⃣  Coletando métricas de recursos..."
kubectl top nodes > "$EVIDENCIAS_DIR/top_nodes.txt" 2>&1 || echo "⚠️  Metrics server não disponível (necessário para HPA)"
kubectl top pods > "$EVIDENCIAS_DIR/top_pods.txt" 2>&1 || echo "⚠️  Metrics server não disponível"
kubectl top pods --containers > "$EVIDENCIAS_DIR/top_containers.txt" 2>&1 || echo "⚠️  Metrics server não disponível"

echo "7️⃣  Coletando informações do Prometheus..."
kubectl get all -n monitoring > "$EVIDENCIAS_DIR/prometheus_all.txt" 2>&1 || echo "Namespace monitoring não encontrado"
kubectl get pods -n monitoring -o wide > "$EVIDENCIAS_DIR/prometheus_pods.txt" 2>&1 || echo "Namespace monitoring não encontrado"
kubectl get configmap -n monitoring prometheus-config -o yaml > "$EVIDENCIAS_DIR/prometheus_config.yaml" 2>&1 || echo "ConfigMap Prometheus não encontrado"

echo "8️⃣  Coletando descrições detalhadas..."
for deploy in module-p module-a module-b; do
    echo "   Descrevendo $deploy..."
    kubectl describe deployment $deploy > "$EVIDENCIAS_DIR/describe_deployment_$deploy.txt" 2>&1 || echo "Deployment $deploy não encontrado"
    kubectl describe service ${deploy}-service > "$EVIDENCIAS_DIR/describe_service_$deploy.txt" 2>&1 || echo "Service ${deploy}-service não encontrado"
    kubectl describe hpa ${deploy}-hpa > "$EVIDENCIAS_DIR/describe_hpa_$deploy.txt" 2>&1 || echo "HPA ${deploy}-hpa não encontrado"
done

echo "9️⃣  Coletando eventos..."
kubectl get events --sort-by='.metadata.creationTimestamp' > "$EVIDENCIAS_DIR/events.txt" 2>&1 || echo "Erro ao coletar eventos"

echo "🔟 Coletando logs dos pods..."
mkdir -p "$EVIDENCIAS_DIR/logs"
for pod in $(kubectl get pods -n default -o jsonpath='{.items[*].metadata.name}' 2>/dev/null); do
    echo "   Coletando logs de $pod..."
    kubectl logs $pod --tail=500 > "$EVIDENCIAS_DIR/logs/${pod}.log" 2>&1 || echo "Erro ao coletar logs de $pod"
done

echo ""
echo "=================================="
echo "✅ Coleta concluída!"
echo "=================================="
echo ""
echo "📁 Evidências salvas em: $EVIDENCIAS_DIR"
echo ""
echo "📋 Arquivos gerados:"
ls -lh "$EVIDENCIAS_DIR"
echo ""
echo "🔍 Para visualizar:"
echo "   cat $EVIDENCIAS_DIR/nodes.txt"
echo "   cat $EVIDENCIAS_DIR/hpa.txt"
echo "   cat $EVIDENCIAS_DIR/top_pods.txt"
echo ""
echo "💡 Próximos passos:"
echo "   1. Execute os testes de carga: cd load-tests && python3 execute_scenarios.py"
echo "   2. Colete evidências novamente durante/após os testes"
echo "   3. Compare os resultados"
echo ""
