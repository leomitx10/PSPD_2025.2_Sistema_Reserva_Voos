#!/usr/bin/env python3
"""
Script base para executar um único cenário de teste de carga
"""

import subprocess
import time
import json
import os
import sys
from datetime import datetime
import requests

# Configurações
HOST = "http://localhost:3000"
RESULTS_DIR = "results"

def print_header(msg):
    print("\n" + "="*80)
    print(f"  {msg}")
    print("="*80)

def print_success(msg):
    print(f"✓ {msg}")

def print_error(msg):
    print(f"✗ {msg}")

def check_service_health():
    """Verifica se o serviço está respondendo"""
    try:
        response = requests.get(f"{HOST}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def collect_docker_stats():
    """Coleta estatísticas dos containers Docker"""
    try:
        result = subprocess.run(
            ["docker", "stats", "--no-stream", "--format", "json"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        stats = []
        for line in result.stdout.strip().split('\n'):
            if line:
                stats.append(json.loads(line))
        return stats
    except Exception as e:
        print_error(f"Erro ao coletar estatísticas Docker: {e}")
        return []

def run_locust_test(scenario_name, scenario_config):
    """Executa um teste com Locust"""
    print_header(f"Executando: {scenario_name}")
    print(f"Descrição: {scenario_config['description']}")
    print(f"Usuários: {scenario_config['users']} | Spawn Rate: {scenario_config['spawn_rate']}/s | Duração: {scenario_config['duration']}")
    print(f"HPA: {'Habilitado' if scenario_config.get('hpa_enabled', False) else 'Desabilitado'}")
    
    # Criar diretório de resultados
    os.makedirs(RESULTS_DIR, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_prefix = f"{RESULTS_DIR}/{scenario_name}_{timestamp}"
    
    # Comando Locust
    cmd = [
        "locust",
        "-f", "locustfile.py",
        "--headless",
        "--host", HOST,
        "-u", str(scenario_config['users']),
        "-r", str(scenario_config['spawn_rate']),
        "-t", scenario_config['duration'],
        "--html", f"{output_prefix}_report.html",
        "--csv", f"{output_prefix}",
        "--loglevel", "ERROR"
    ]
    
    try:
        # Coletar estatísticas iniciais
        stats_before = collect_docker_stats()
        
        print("\n⏳ Teste em andamento...")
        
        # Executar teste (sem mostrar output detalhado)
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        process.wait()
        
        # Coletar estatísticas finais
        time.sleep(2)
        stats_after = collect_docker_stats()
        
        # Salvar estatísticas Docker
        stats_file = f"{output_prefix}_docker_stats.json"
        with open(stats_file, 'w') as f:
            json.dump({
                'before': stats_before,
                'after': stats_after,
                'scenario': scenario_config
            }, f, indent=2)
        
        if process.returncode == 0:
            # Ler e exibir métricas do CSV
            print_test_metrics(output_prefix)
            return True
        else:
            print_error(f"Teste falhou com código {process.returncode}")
            return False
            
    except Exception as e:
        print_error(f"Erro ao executar teste: {e}")
        return False

def print_test_metrics(output_prefix):
    """Lê e exibe as métricas principais do teste"""
    try:
        stats_file = f"{output_prefix}_stats.csv"
        if os.path.exists(stats_file):
            with open(stats_file, 'r') as f:
                lines = f.readlines()
                if len(lines) > 1:
                    # Pegar a linha de totais (última linha antes de distribuição)
                    for line in lines[1:]:
                        if line.startswith('Aggregated') or line.startswith('"Aggregated"'):
                            parts = line.strip().split(',')
                            if len(parts) >= 10:
                                print(f"\n📊 RESULTADOS:")
                                print(f"   Requisições: {parts[1]}")
                                print(f"   Falhas: {parts[2]} ({parts[3]})")
                                print(f"   Tempo Médio: {parts[4]} ms")
                                print(f"   Tempo Mínimo: {parts[5]} ms")
                                print(f"   Tempo Máximo: {parts[6]} ms")
                                print(f"   Throughput: {parts[10]} req/s")
                            break
        print_success(f"Relatório HTML: {output_prefix}_report.html")
        print_success(f"Dados CSV: {output_prefix}_stats.csv")
        print_success(f"Docker Stats: {output_prefix}_docker_stats.json")
    except Exception as e:
        print_error(f"Erro ao ler métricas: {e}")

def run_scenario(scenario_name, scenario_config):
    """Executa um cenário específico"""
    print_header(f"TESTE DE CARGA - {scenario_name.upper()}")
    print(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Verificar se o serviço está disponível
    if not check_service_health():
        print_error("Serviço não está respondendo!")
        print("Verifique se os containers estão rodando: docker-compose ps")
        return 1
    
    print_success("Serviço disponível\n")
    
    # Executar cenário
    success = run_locust_test(scenario_name, scenario_config)
    
    # Resultado final
    print_header("Resultado")
    if success:
        print_success(f"✓ Cenário '{scenario_name}' executado com sucesso!")
        return 0
    else:
        print_error(f"✗ Cenário '{scenario_name}' falhou!")
        return 1

if __name__ == "__main__":
    print("Este é um módulo base. Execute os scripts individuais de cada cenário.")
    sys.exit(1)
