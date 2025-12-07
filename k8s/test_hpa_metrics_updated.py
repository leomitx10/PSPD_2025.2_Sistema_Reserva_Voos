#!/usr/bin/env python3
"""
Script para verificar se as métricas de HPA estão disponíveis no Prometheus
"""
import requests
import json
from datetime import datetime

# Configuração
PROMETHEUS_URL = "http://localhost:9090"

def query_prometheus(query):
    """Executa uma query no Prometheus"""
    try:
        response = requests.get(
            f"{PROMETHEUS_URL}/api/v1/query",
            params={'query': query},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'success':
                return data['data']['result']
        return None
    except Exception as e:
        print(f"❌ Erro ao consultar Prometheus: {e}")
        return None

def check_metric(name, query, description):
    """Verifica se uma métrica está disponível"""
    print(f"\n🔍 Verificando: {name}")
    print(f"   {description}")
    
    result = query_prometheus(query)
    
    if result is None:
        print(f"   ❌ Erro ao executar query")
        return False
    elif len(result) == 0:
        print(f"   ⚠️  Nenhum dado encontrado")
        return False
    else:
        print(f"   ✅ Dados disponíveis ({len(result)} métricas)")
        for metric in result[:3]:  # Mostra até 3 exemplos
            labels = metric.get('metric', {})
            value = metric.get('value', [None, None])[1]
            
            # Formatar labels
            label_str = ', '.join([f"{k}={v}" for k, v in labels.items() if k != '__name__'])
            print(f"      • {label_str[:80]}: {value}")
        
        if len(result) > 3:
            print(f"      ... e mais {len(result) - 3} métricas")
        return True

def main():
    print("=" * 70)
    print("Verificação de Métricas de HPA no Prometheus")
    print("=" * 70)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Prometheus URL: {PROMETHEUS_URL}")
    
    # Verificar conectividade com Prometheus
    print("\n📡 Verificando conectividade com Prometheus...")
    try:
        response = requests.get(f"{PROMETHEUS_URL}/-/healthy", timeout=5)
        if response.status_code == 200:
            print("   ✅ Prometheus está acessível")
        else:
            print(f"   ❌ Prometheus retornou status {response.status_code}")
            print("   💡 Execute: kubectl port-forward -n monitoring svc/prometheus 9090:9090")
            return
    except Exception as e:
        print(f"   ❌ Não foi possível conectar ao Prometheus: {e}")
        print("   💡 Execute: kubectl port-forward -n monitoring svc/prometheus 9090:9090")
        return
    
    metrics_ok = 0
    metrics_total = 0
    
    # Métricas Essenciais do HPA
    print("\n" + "=" * 70)
    print("📊 MÉTRICAS ESSENCIAIS DO HPA")
    print("=" * 70)
    
    metrics_total += 1
    if check_metric(
        "CPU Target Utilization",
        'kube_horizontalpodautoscaler_spec_target_metric{metric_name="cpu", metric_target_type="utilization"}',
        "Threshold de CPU configurado no HPA (deveria ser 50%)"
    ):
        metrics_ok += 1
    
    metrics_total += 1
    if check_metric(
        "Réplicas Desejadas",
        'kube_horizontalpodautoscaler_status_desired_replicas',
        "Número de réplicas que o HPA quer ter"
    ):
        metrics_ok += 1
    
    metrics_total += 1
    if check_metric(
        "Réplicas Atuais",
        'kube_horizontalpodautoscaler_status_current_replicas',
        "Número de réplicas atualmente rodando"
    ):
        metrics_ok += 1
    
    metrics_total += 1
    if check_metric(
        "Min/Max Réplicas",
        'kube_horizontalpodautoscaler_spec_min_replicas',
        "Configuração de réplicas mínimas"
    ):
        metrics_ok += 1
    
    # Métricas de CPU e Memória
    print("\n" + "=" * 70)
    print("💻 MÉTRICAS DE CPU E MEMÓRIA")
    print("=" * 70)
    
    metrics_total += 1
    if check_metric(
        "Uso de CPU por Pod",
        'sum(rate(container_cpu_usage_seconds_total{pod=~"voos-service.*|hoteis-service.*|api-gateway.*", container!="POD"}[5m])) by (pod) * 1000',
        "CPU utilizada por cada pod (millicores)"
    ):
        metrics_ok += 1
    
    metrics_total += 1
    if check_metric(
        "CPU Request por Pod",
        'sum(kube_pod_container_resource_requests{resource="cpu", pod=~"voos-service.*|hoteis-service.*|api-gateway.*"}) by (pod)',
        "CPU solicitada (request) por pod"
    ):
        metrics_ok += 1
    
    metrics_total += 1
    if check_metric(
        "% CPU Usado vs Request",
        '100 * sum(rate(container_cpu_usage_seconds_total{pod=~"voos-service.*|hoteis-service.*|api-gateway.*", container!="POD"}[5m])) by (pod) / sum(kube_pod_container_resource_requests{resource="cpu", pod=~"voos-service.*|hoteis-service.*|api-gateway.*"}) by (pod)',
        "Percentual de CPU usado em relação ao request"
    ):
        metrics_ok += 1
    
    metrics_total += 1
    if check_metric(
        "Uso de Memória por Pod",
        'sum(container_memory_working_set_bytes{pod=~"voos-service.*|hoteis-service.*|api-gateway.*", container!="POD"}) by (pod)',
        "Memória utilizada por cada pod"
    ):
        metrics_ok += 1
    
    # Métricas de Elasticidade
    print("\n" + "=" * 70)
    print("📈 MÉTRICAS DE ELASTICIDADE")
    print("=" * 70)
    
    metrics_total += 1
    if check_metric(
        "Número de Réplicas por Deployment",
        'kube_deployment_status_replicas{deployment=~"voos-service|hoteis-service|api-gateway"}',
        "Réplicas atuais de cada deployment"
    ):
        metrics_ok += 1
    
    metrics_total += 1
    if check_metric(
        "HPA Able to Scale",
        'kube_horizontalpodautoscaler_status_condition{condition="AbleToScale"}',
        "Se o HPA consegue escalar (1 = sim, 0 = não)"
    ):
        metrics_ok += 1
    
    metrics_total += 1
    if check_metric(
        "HPA Scaling Active",
        'kube_horizontalpodautoscaler_status_condition{condition="ScalingActive"}',
        "Se o escalamento está ativo (1 = sim, 0 = não)"
    ):
        metrics_ok += 1
    
    metrics_total += 1
    if check_metric(
        "Diferença Desejado vs Atual",
        'kube_horizontalpodautoscaler_status_desired_replicas - kube_horizontalpodautoscaler_status_current_replicas',
        "Diferença entre réplicas desejadas e atuais (>0 = escalando)"
    ):
        metrics_ok += 1
    
    # Resumo
    print("\n" + "=" * 70)
    print("📊 RESUMO")
    print("=" * 70)
    print(f"Métricas verificadas: {metrics_total}")
    print(f"Métricas disponíveis: {metrics_ok}")
    print(f"Métricas ausentes: {metrics_total - metrics_ok}")
    
    percentage = (metrics_ok / metrics_total) * 100 if metrics_total > 0 else 0
    
    print(f"\nTaxa de sucesso: {percentage:.1f}%")
    
    if percentage == 100:
        print("\n✅ TODAS AS MÉTRICAS ESTÃO DISPONÍVEIS!")
        print("   O sistema está pronto para validar elasticidade.")
    elif percentage >= 75:
        print("\n⚠️  A MAIORIA DAS MÉTRICAS ESTÁ DISPONÍVEL")
        print("   O sistema pode validar elasticidade, mas algumas métricas estão faltando.")
    else:
        print("\n❌ MUITAS MÉTRICAS ESTÃO FALTANDO")
        print("   Verifique a configuração do Prometheus e do kube-state-metrics.")
        print("\n💡 Passos para corrigir:")
        print("   1. Aplicar a configuração atualizada do Prometheus:")
        print("      kubectl apply -f prometheus-config.yaml")
        print("   2. Reiniciar o Prometheus:")
        print("      kubectl rollout restart deployment/prometheus -n monitoring")
        print("   3. Verificar se kube-state-metrics está rodando:")
        print("      kubectl get pods -n monitoring -l app=kube-state-metrics")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()
