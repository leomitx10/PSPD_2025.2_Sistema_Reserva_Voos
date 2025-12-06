#!/usr/bin/env python3
"""
Script para executar cenários de teste de carga automaticamente
Coleta métricas e gera relatórios
"""

import subprocess
import time
import json
import os
from datetime import datetime
import requests
from scenarios import SCENARIOS

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
    print(f"Usuários: {scenario_config['users']}")
    print(f"Spawn Rate: {scenario_config['spawn_rate']}/s")
    print(f"Duração: {scenario_config['duration']}")
    
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
        "--loglevel", "INFO"
    ]
    
    print(f"\nIniciando teste às {datetime.now().strftime('%H:%M:%S')}...")
    
    try:
        # Coletar estatísticas iniciais
        stats_before = collect_docker_stats()
        
        # Executar teste
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        # Mostrar output em tempo real
        for line in process.stdout:
            print(line, end='')
        
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
            print_success(f"Teste concluído com sucesso!")
            print_success(f"Relatório HTML: {output_prefix}_report.html")
            print_success(f"Dados CSV: {output_prefix}_stats.csv")
            print_success(f"Estatísticas Docker: {stats_file}")
            return True
        else:
            print_error(f"Teste falhou com código {process.returncode}")
            return False
            
    except Exception as e:
        print_error(f"Erro ao executar teste: {e}")
        return False

def generate_summary():
    """Gera um resumo dos testes executados"""
    print_header("Gerando Resumo dos Testes")
    
    summary_file = f"{RESULTS_DIR}/summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    with open(summary_file, 'w') as f:
        f.write("="*80 + "\n")
        f.write("RESUMO DOS TESTES DE CARGA\n")
        f.write(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*80 + "\n\n")
        
        # Listar arquivos gerados
        f.write("Arquivos Gerados:\n")
        for file in sorted(os.listdir(RESULTS_DIR)):
            if file.endswith(('.html', '.csv', '.json')):
                filepath = os.path.join(RESULTS_DIR, file)
                size = os.path.getsize(filepath)
                f.write(f"  - {file} ({size} bytes)\n")
        
        f.write("\n" + "="*80 + "\n")
        f.write("Para visualizar os resultados:\n")
        f.write(f"  1. Abra os arquivos HTML em {RESULTS_DIR}/*_report.html\n")
        f.write(f"  2. Analise os CSVs em {RESULTS_DIR}/*_stats.csv\n")
        f.write(f"  3. Verifique as estatísticas Docker em {RESULTS_DIR}/*_docker_stats.json\n")
    
    print_success(f"Resumo salvo em: {summary_file}")
    
    # Mostrar resumo no terminal
    with open(summary_file, 'r') as f:
        print("\n" + f.read())

def main():
    print_header("Sistema de Testes de Carga - PSPD 2025.2")
    print(f"Host alvo: {HOST}")
    
    # Verificar se o serviço está disponível
    print("\nVerificando disponibilidade do serviço...")
    if not check_service_health():
        print_error("Serviço não está respondendo!")
        print("Verifique se os containers estão rodando: docker-compose ps")
        return 1
    
    print_success("Serviço está disponível e respondendo")
    
    # Executar cada cenário
    results = {}
    for scenario_name, scenario_config in SCENARIOS.items():
        success = run_locust_test(scenario_name, scenario_config)
        results[scenario_name] = success
        
        # Aguardar entre testes
        if scenario_name != list(SCENARIOS.keys())[-1]:
            wait_time = 5
            print(f"\nAguardando {wait_time} segundos antes do próximo teste...")
            time.sleep(wait_time)
    
    # Gerar resumo
    generate_summary()
    
    # Mostrar resultados finais
    print_header("Resultados Finais")
    for scenario_name, success in results.items():
        status = "✓ SUCESSO" if success else "✗ FALHA"
        print(f"{status}: {scenario_name}")
    
    total = len(results)
    passed = sum(results.values())
    print(f"\nTotal: {passed}/{total} cenários executados com sucesso")
    
    return 0 if all(results.values()) else 1

if __name__ == "__main__":
    exit(main())
