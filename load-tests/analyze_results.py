#!/usr/bin/env python3
"""
Script de Análise de Resultados dos Testes de Carga
Gera resumo comparativo e estatísticas dos cenários executados
"""

import os
import csv
import json
from datetime import datetime
from pathlib import Path

RESULTS_DIR = Path(__file__).parent / "results"


def parse_csv_stats(csv_file):
    """Parse arquivo CSV de estatísticas do Locust"""
    stats = {}
    try:
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['Name'] == 'Aggregated':
                    stats = {
                        'total_requests': int(row['Request Count']) if row['Request Count'] else 0,
                        'total_failures': int(row['Failure Count']) if row['Failure Count'] else 0,
                        'avg_response_time': float(row['Average Response Time']) if row['Average Response Time'] else 0,
                        'min_response_time': float(row['Min Response Time']) if row['Min Response Time'] else 0,
                        'max_response_time': float(row['Max Response Time']) if row['Max Response Time'] else 0,
                        'median_response_time': float(row['Median Response Time']) if row['Median Response Time'] else 0,
                        'requests_per_sec': float(row['Requests/s']) if row['Requests/s'] else 0,
                    }
    except Exception as e:
        print(f"Erro ao parsear {csv_file}: {e}")
    return stats


def parse_docker_stats(json_file):
    """Parse arquivo JSON de estatísticas Docker"""
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
            return data
    except Exception as e:
        print(f"Erro ao parsear {json_file}: {e}")
    return {}


def analyze_scenario(scenario_name):
    """Analisa resultados de um cenário específico"""
    print(f"\n{'='*80}")
    print(f"Análise: {scenario_name}")
    print(f"{'='*80}")
    
    # Buscar arquivos mais recentes do cenário
    pattern = f"{scenario_name}_*_stats.csv"
    csv_files = sorted(RESULTS_DIR.glob(pattern), key=os.path.getmtime, reverse=True)
    
    if not csv_files:
        print(f"⚠️  Nenhum resultado encontrado para {scenario_name}")
        return None
    
    latest_csv = csv_files[0]
    timestamp = latest_csv.stem.split('_')[-2] + '_' + latest_csv.stem.split('_')[-1]
    
    # Parse CSV
    stats = parse_csv_stats(latest_csv)
    
    if not stats:
        print(f"⚠️  Erro ao processar estatísticas")
        return None
    
    # Parse Docker stats se disponível
    docker_file = latest_csv.parent / f"{scenario_name}_{timestamp}_docker_stats.json"
    docker_stats = parse_docker_stats(docker_file) if docker_file.exists() else {}
    
    # Calcular métricas
    failure_rate = (stats['total_failures'] / stats['total_requests'] * 100) if stats['total_requests'] > 0 else 0
    success_rate = 100 - failure_rate
    
    print(f"\n📊 Estatísticas Gerais:")
    print(f"  • Total de Requisições: {stats['total_requests']}")
    print(f"  • Requisições com Sucesso: {stats['total_requests'] - stats['total_failures']}")
    print(f"  • Requisições com Falha: {stats['total_failures']}")
    print(f"  • Taxa de Sucesso: {success_rate:.2f}%")
    print(f"  • Taxa de Falha: {failure_rate:.2f}%")
    print(f"  • Throughput: {stats['requests_per_sec']:.2f} req/s")
    
    print(f"\n⏱️  Tempos de Resposta:")
    print(f"  • Mínimo: {stats['min_response_time']:.0f} ms")
    print(f"  • Médio: {stats['avg_response_time']:.0f} ms")
    print(f"  • Mediana: {stats['median_response_time']:.0f} ms")
    print(f"  • Máximo: {stats['max_response_time']:.0f} ms")
    
    if docker_stats:
        print(f"\n🐳 Estatísticas Docker:")
        scenario_config = docker_stats.get('scenario', {})
        print(f"  • Configuração: {scenario_config.get('description', 'N/A')}")
        print(f"  • Usuários: {scenario_config.get('users', 'N/A')}")
        print(f"  • Spawn Rate: {scenario_config.get('spawn_rate', 'N/A')}")
        print(f"  • Duração: {scenario_config.get('duration', 'N/A')}")
    
    return {
        'scenario': scenario_name,
        'timestamp': timestamp,
        **stats,
        'failure_rate': failure_rate,
        'success_rate': success_rate
    }


def generate_comparative_report(scenarios):
    """Gera relatório comparativo entre cenários"""
    print(f"\n{'='*80}")
    print("RELATÓRIO COMPARATIVO")
    print(f"{'='*80}\n")
    
    results = []
    for scenario in scenarios:
        result = analyze_scenario(scenario)
        if result:
            results.append(result)
    
    if not results:
        print("⚠️  Nenhum resultado válido para comparação")
        return
    
    print(f"\n{'='*80}")
    print("TABELA COMPARATIVA")
    print(f"{'='*80}\n")
    
    # Cabeçalho
    print(f"{'Cenário':<30} {'Req':<8} {'Falhas':<8} {'Taxa Suc':<10} {'Throughput':<12} {'Tempo Médio':<12}")
    print(f"{'-'*30} {'-'*8} {'-'*8} {'-'*10} {'-'*12} {'-'*12}")
    
    # Dados
    for r in results:
        print(f"{r['scenario']:<30} {r['total_requests']:<8} {r['total_failures']:<8} "
              f"{r['success_rate']:<10.2f} {r['requests_per_sec']:<12.2f} {r['avg_response_time']:<12.0f}")
    
    print(f"\n{'='*80}")
    print("RANKING POR PERFORMANCE")
    print(f"{'='*80}\n")
    
    # Melhor throughput
    best_throughput = max(results, key=lambda x: x['requests_per_sec'])
    print(f"🏆 Maior Throughput: {best_throughput['scenario']}")
    print(f"   {best_throughput['requests_per_sec']:.2f} req/s")
    
    # Menor latência
    best_latency = min(results, key=lambda x: x['avg_response_time'])
    print(f"\n⚡ Menor Latência Média: {best_latency['scenario']}")
    print(f"   {best_latency['avg_response_time']:.0f} ms")
    
    # Maior confiabilidade
    best_reliability = max(results, key=lambda x: x['success_rate'])
    print(f"\n✅ Maior Confiabilidade: {best_reliability['scenario']}")
    print(f"   {best_reliability['success_rate']:.2f}% de sucesso")
    
    # Salvar relatório
    report_file = RESULTS_DIR / f"comparative_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_file, 'w') as f:
        f.write("RELATÓRIO COMPARATIVO DE CENÁRIOS DE TESTE\n")
        f.write(f"Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        for r in results:
            f.write(f"\n{'='*80}\n")
            f.write(f"Cenário: {r['scenario']}\n")
            f.write(f"{'='*80}\n")
            f.write(f"Total Requisições: {r['total_requests']}\n")
            f.write(f"Taxa de Sucesso: {r['success_rate']:.2f}%\n")
            f.write(f"Throughput: {r['requests_per_sec']:.2f} req/s\n")
            f.write(f"Tempo Médio: {r['avg_response_time']:.0f} ms\n")
            f.write(f"Tempo Mínimo: {r['min_response_time']:.0f} ms\n")
            f.write(f"Tempo Máximo: {r['max_response_time']:.0f} ms\n")
    
    print(f"\n📄 Relatório salvo em: {report_file}")


def main():
    """Função principal"""
    print(f"\n{'='*80}")
    print("ANÁLISE DE RESULTADOS DOS TESTES DE CARGA")
    print(f"{'='*80}")
    
    scenarios = [
        "cenario_1_baseline",
        "cenario_2_moderate",
        "cenario_3_high_load",
        "cenario_4_spike",
        "cenario_5_stress"
    ]
    
    generate_comparative_report(scenarios)
    
    print(f"\n{'='*80}")
    print("Análise concluída!")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()
