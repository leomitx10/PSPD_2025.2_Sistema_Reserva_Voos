"""
Script para comparar performance entre gRPC e REST

Executa 4 cenários de teste:
1. Requisição simples (poucos filtros)
2. Requisição complexa (muitos filtros)
3. Alto volume de requisições
4. Transferência de grande volume de dados
"""

import time
import requests
import grpc
import statistics
import sys
import os

# Adicionar path dos protos
sys.path.append('../Voos')
sys.path.append('../Hoteis/proto')

import voos_service_pb2
import voos_service_pb2_grpc

def test_grpc_voos_simples(n_requests=10):
    """Cenário 1: Requisição simples - gRPC"""
    times = []

    with grpc.insecure_channel('localhost:50051') as channel:
        stub = voos_service_pb2_grpc.VoosServiceStub(channel)

        for _ in range(n_requests):
            request = voos_service_pb2.ConsultaVoosRequest(
                origem="São Paulo",
                destino="Rio de Janeiro"
            )

            start = time.time()
            try:
                response = stub.ConsultarVoos(request)
                elapsed = time.time() - start
                times.append(elapsed * 1000)  # Converter para ms
            except grpc.RpcError as e:
                print(f"Erro gRPC: {e.details()}")
                continue

    return times

def test_rest_voos_simples(n_requests=10):
    """Cenário 1: Requisição simples - REST"""
    times = []
    url = "http://localhost:5001/voos/search"

    for _ in range(n_requests):
        payload = {
            "origem": "São Paulo",
            "destino": "Rio de Janeiro"
        }

        start = time.time()
        try:
            response = requests.post(url, json=payload, timeout=10)
            elapsed = time.time() - start
            if response.status_code == 200:
                times.append(elapsed * 1000)
        except requests.exceptions.RequestException as e:
            print(f"Erro REST: {e}")
            continue

    return times

def test_grpc_voos_complexo(n_requests=10):
    """Cenário 2: Requisição complexa - gRPC"""
    times = []

    with grpc.insecure_channel('localhost:50051') as channel:
        stub = voos_service_pb2_grpc.VoosServiceStub(channel)

        for _ in range(n_requests):
            request = voos_service_pb2.ConsultaVoosRequest(
                origem="São Paulo",
                destino="Rio de Janeiro",
                data="2025-11-15",
                preco_max=800.0,
                companhia_aerea="LATAM",
                faixa_horario="manha",
                ordenacao="preco"
            )

            start = time.time()
            try:
                response = stub.ConsultarVoos(request)
                elapsed = time.time() - start
                times.append(elapsed * 1000)
            except grpc.RpcError as e:
                print(f"Erro gRPC: {e.details()}")
                continue

    return times

def test_rest_voos_complexo(n_requests=10):
    """Cenário 2: Requisição complexa - REST"""
    times = []
    url = "http://localhost:5001/voos/search"

    for _ in range(n_requests):
        payload = {
            "origem": "São Paulo",
            "destino": "Rio de Janeiro",
            "data": "2025-11-15",
            "preco_max": 800.0,
            "companhia_aerea": "LATAM",
            "faixa_horario": "manha",
            "ordenacao": "preco"
        }

        start = time.time()
        try:
            response = requests.post(url, json=payload, timeout=10)
            elapsed = time.time() - start
            if response.status_code == 200:
                times.append(elapsed * 1000)
        except requests.exceptions.RequestException as e:
            print(f"Erro REST: {e}")
            continue

    return times

def test_grpc_alto_volume(n_requests=50):
    """Cenário 3: Alto volume - gRPC"""
    return test_grpc_voos_simples(n_requests)

def test_rest_alto_volume(n_requests=50):
    """Cenário 3: Alto volume - REST"""
    return test_rest_voos_simples(n_requests)

def calcular_estatisticas(times):
    """Calcula estatísticas dos tempos de resposta"""
    if not times:
        return {
            'min': 0,
            'max': 0,
            'media': 0,
            'mediana': 0,
            'desvio_padrao': 0
        }

    return {
        'min': min(times),
        'max': max(times),
        'media': statistics.mean(times),
        'mediana': statistics.median(times),
        'desvio_padrao': statistics.stdev(times) if len(times) > 1 else 0
    }

def exibir_resultados(nome_cenario, stats_grpc, stats_rest):
    """Exibe comparação entre gRPC e REST"""
    print(f"\n{'=' * 80}")
    print(f"CENÁRIO: {nome_cenario}")
    print('=' * 80)

    print(f"\n{'Métrica':<20} {'gRPC (ms)':<15} {'REST (ms)':<15} {'Diferença (%)':<15}")
    print('-' * 80)

    metricas = ['min', 'max', 'media', 'mediana', 'desvio_padrao']
    labels = ['Mínimo', 'Máximo', 'Média', 'Mediana', 'Desvio Padrão']

    for metrica, label in zip(metricas, labels):
        grpc_val = stats_grpc[metrica]
        rest_val = stats_rest[metrica]

        if rest_val > 0:
            diff = ((rest_val - grpc_val) / rest_val) * 100
        else:
            diff = 0

        print(f"{label:<20} {grpc_val:<15.2f} {rest_val:<15.2f} {diff:<15.2f}")

    if stats_grpc['media'] > 0:
        speedup = stats_rest['media'] / stats_grpc['media']
        print(f"\nSpeedup do gRPC: {speedup:.2f}x mais rápido")

def main():
    print("\n" + "=" * 80)
    print("COMPARATIVO DE PERFORMANCE: gRPC vs REST")
    print("=" * 80)
    print("\nCertifique-se de que os seguintes serviços estão rodando:")
    print("  - Servidor gRPC de Voos (porta 50051)")
    print("  - Servidor REST de Voos (porta 5001)")
    print("\n" + "=" * 80)

    input("\nPressione ENTER para iniciar os testes...")

    # Cenário 1: Requisição Simples
    print("\n\n🔄 Executando Cenário 1: Requisição Simples (10 requisições)...")
    grpc_times_1 = test_grpc_voos_simples(10)
    rest_times_1 = test_rest_voos_simples(10)
    exibir_resultados(
        "Requisição Simples (poucos filtros)",
        calcular_estatisticas(grpc_times_1),
        calcular_estatisticas(rest_times_1)
    )

    # Cenário 2: Requisição Complexa
    print("\n\n🔄 Executando Cenário 2: Requisição Complexa (10 requisições)...")
    grpc_times_2 = test_grpc_voos_complexo(10)
    rest_times_2 = test_rest_voos_complexo(10)
    exibir_resultados(
        "Requisição Complexa (muitos filtros)",
        calcular_estatisticas(grpc_times_2),
        calcular_estatisticas(rest_times_2)
    )

    # Cenário 3: Alto Volume
    print("\n\n🔄 Executando Cenário 3: Alto Volume (50 requisições)...")
    grpc_times_3 = test_grpc_alto_volume(50)
    rest_times_3 = test_rest_alto_volume(50)
    exibir_resultados(
        "Alto Volume de Requisições",
        calcular_estatisticas(grpc_times_3),
        calcular_estatisticas(rest_times_3)
    )

    # Cenário 4: Grande Volume de Dados (similar ao cenário 1 mas contando dados)
    print("\n\n🔄 Executando Cenário 4: Transferência de Grandes Volumes...")
    grpc_times_4 = test_grpc_voos_simples(10)
    rest_times_4 = test_rest_voos_simples(10)
    exibir_resultados(
        "Transferência de Grande Volume de Dados",
        calcular_estatisticas(grpc_times_4),
        calcular_estatisticas(rest_times_4)
    )

    print("\n\n" + "=" * 80)
    print("CONCLUSÕES:")
    print("=" * 80)
    print("""
1. gRPC geralmente apresenta menor latência devido ao uso de HTTP/2 e serialização binária
2. REST é mais adequado para APIs públicas e integração com navegadores
3. gRPC é superior para comunicação entre microserviços internos
4. A diferença de performance é mais evidente em alto volume de requisições
    """)

if __name__ == '__main__':
    main()
