#!/usr/bin/env python3
"""
Script para testar queries do Prometheus - CPU e Memória por Pod/Container
"""
import time
import subprocess
import sys

def test_prometheus_query(query, description):
    """Testa uma query do Prometheus"""
    print(f"\n{'='*70}")
    print(f"🔍 Testando: {description}")
    print(f"Query: {query}")
    print(f"{'='*70}")
    
    cmd = f'''kubectl exec -n monitoring deployment/prometheus -- \
wget -qO- "http://localhost:9090/api/v1/query?query={query}" 2>/dev/null'''
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 and result.stdout:
            import json
            try:
                data = json.loads(result.stdout)
                if data.get('status') == 'success':
                    results = data.get('data', {}).get('result', [])
                    if results:
                        print(f"✅ Sucesso! Encontrados {len(results)} resultados")
                        # Mostra os primeiros 3 resultados
                        for i, r in enumerate(results[:3], 1):
                            metric = r.get('metric', {})
                            value = r.get('value', [None, 'N/A'])[1]
                            print(f"  {i}. {metric.get('pod', metric.get('namespace', 'N/A'))}: {value}")
                        if len(results) > 3:
                            print(f"  ... e mais {len(results) - 3} resultados")
                        return True
                    else:
                        print(f"⚠️  Query executada mas sem resultados")
                        return False
                else:
                    error = data.get('error', 'Erro desconhecido')
                    print(f"❌ Erro na query: {error}")
                    return False
            except json.JSONDecodeError:
                print(f"❌ Erro ao parsear resposta JSON")
                return False
        else:
            print(f"❌ Erro ao executar comando: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"❌ Timeout ao executar query")
        return False
    except Exception as e:
        print(f"❌ Exceção: {str(e)}")
        return False


def main():
    print("\n" + "="*70)
    print("  TESTE DE QUERIES PROMETHEUS - CPU E MEMÓRIA POR POD/CONTAINER")
    print("="*70)
    
    # Aguardar o Prometheus estar pronto
    print("\n⏳ Aguardando Prometheus estar pronto...")
    time.sleep(5)
    
    queries = [
        # Métricas básicas de container
        ("container_cpu_usage_seconds_total", 
         "Verificar se cAdvisor está coletando métricas de CPU"),
        
        ("container_memory_working_set_bytes", 
         "Verificar se cAdvisor está coletando métricas de Memória"),
        
        # CPU por container
        ('sum(rate(container_cpu_usage_seconds_total{container!="",container!="POD"}[5m]))by(pod,container)', 
         "CPU por container (excluindo POD)"),
        
        # Memória por container
        ('container_memory_working_set_bytes{container!="",container!="POD"}', 
         "Memória Working Set por container"),
        
        # CPU por pod (agregado)
        ('sum(rate(container_cpu_usage_seconds_total{container!="",container!="POD"}[5m]))by(pod,namespace)', 
         "CPU por pod (soma de containers)"),
        
        # Memória por pod (agregado)  
        ('sum(container_memory_working_set_bytes{container!="",container!="POD"})by(pod,namespace)', 
         "Memória por pod (soma de containers)"),
        
        # Métricas de HPA via kube-state-metrics
        ('kube_horizontalpodautoscaler_status_current_replicas', 
         "Réplicas atuais do HPA"),
        
        ('kube_pod_info', 
         "Informações de pods via kube-state-metrics"),
    ]
    
    results = []
    for query, description in queries:
        success = test_prometheus_query(query, description)
        results.append((description, success))
        time.sleep(1)  # Pequeno delay entre queries
    
    # Resumo
    print("\n" + "="*70)
    print("  RESUMO DOS TESTES")
    print("="*70)
    
    successful = sum(1 for _, success in results if success)
    total = len(results)
    
    for description, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {description}")
    
    print(f"\n📊 Resultado: {successful}/{total} queries funcionando")
    
    if successful == total:
        print("\n🎉 TODOS OS TESTES PASSARAM! Métricas estão sendo coletadas corretamente.")
        return 0
    elif successful > 0:
        print("\n⚠️  ALGUNS TESTES FALHARAM. Verifique a configuração do Prometheus.")
        return 1
    else:
        print("\n❌ TODOS OS TESTES FALHARAM. Verifique se o Prometheus está rodando corretamente.")
        return 2


if __name__ == "__main__":
    sys.exit(main())
