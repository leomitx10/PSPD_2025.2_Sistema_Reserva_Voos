"""
Script para comparar performance entre gRPC e REST

Executa 6 cenários de teste demonstrando os 4 tipos de comunicação gRPC:
1. Unary RPC - Requisição simples (Consultar Voos)
2. Unary RPC - Requisição complexa (Consultar Voos com filtros)
3. Server Streaming RPC - Monitoramento de Voo (tempo real)
4. Client Streaming RPC - Finalizar Compra (carrinho)
5. Bidirectional Streaming RPC - Chat de Suporte
6. Alto volume de requisições Unary
"""

import time
import requests
import grpc
import statistics
import sys
import os
import threading
import json

sys.path.append('../module-a/proto')
sys.path.append('../module-b/proto')
sys.path.append('.')  

try:
    import voos_service_pb2
    import voos_service_pb2_grpc
except ImportError:
    print("Aviso: Protos de voos não encontrados.")
    voos_service_pb2 = None
    voos_service_pb2_grpc = None

try:
    import hotel_pb2
    import hotel_pb2_grpc
except ImportError:
    print("Aviso: Protos de hotel não encontrados. Alguns testes serão ignorados.")
    hotel_pb2 = None
    hotel_pb2_grpc = None

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
                times.append(elapsed * 1000)  
            except grpc.RpcError as e:
                print(f"Erro gRPC: {e.details()}")
                continue

    return times

def test_rest_voos_simples(n_requests=10):
    times = []
    url = "http://localhost:3000/api/flights/search"

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
    times = []
    url = "http://localhost:3000/api/flights/search"

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

def test_grpc_server_streaming(n_requests=5):
    times = []

    with grpc.insecure_channel('localhost:50051') as channel:
        stub = voos_service_pb2_grpc.VoosServiceStub(channel)

        for i in range(n_requests):
            request = voos_service_pb2.MonitorarVooRequest(
                numero_voo=f"LA{3000 + i}"
            )

            start = time.time()
            updates_received = 0

            try:
                for update in stub.MonitorarVoo(request):
                    updates_received += 1
                    if update.progresso_percentual >= 100:
                        elapsed = time.time() - start
                        times.append(elapsed * 1000)
                        break
            except grpc.RpcError as e:
                print(f"Erro gRPC Streaming: {e.details()}")
                continue

    return times

def test_rest_server_streaming(n_requests=5):
    times = []
    url = "http://localhost:3000/api/flights/monitor"

    for i in range(n_requests):
        numero_voo = f"LA{3000 + i}"

        start = time.time()
        try:
            response = requests.get(f"{url}/{numero_voo}", stream=True, timeout=30)

            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        decoded = line.decode('utf-8')
                        if decoded.startswith('data: '):
                            data = json.loads(decoded[6:])
                            if data.get('progresso_percentual', 0) >= 100:
                                elapsed = time.time() - start
                                times.append(elapsed * 1000)
                                break
        except Exception as e:
            print(f"Erro REST SSE: {e}")
            continue

    return times

def test_grpc_client_streaming(n_requests=5):
    if not hotel_pb2:
        return []

    times = []

    with grpc.insecure_channel('localhost:50052') as channel:
        stub = hotel_pb2_grpc.HotelServiceStub(channel)

        for _ in range(n_requests):
            start = time.time()

            try:
                def item_generator():
                    items = [
                        {"tipo": "voo", "id": "LA3000", "detalhes": "SP-RJ", "preco": 450.0},
                        {"tipo": "hotel", "id": "HTL001", "detalhes": "Copacabana Palace", "preco": 800.0},
                        {"tipo": "pacote", "id": "PKG001", "detalhes": "Pacote Completo", "preco": 1200.0}
                    ]

                    for item in items:
                        yield hotel_pb2.ItemCarrinho(
                            tipo=item["tipo"],
                            id=item["id"],
                            detalhes=item["detalhes"],
                            preco=item["preco"]
                        )

                response = stub.FinalizarCompra(item_generator())
                elapsed = time.time() - start

                if response.sucesso:
                    times.append(elapsed * 1000)
            except grpc.RpcError as e:
                print(f"Erro gRPC Client Streaming: {e.details()}")
                continue

    return times

def test_rest_client_streaming(n_requests=5):
    times = []
    url = "http://localhost:3000/api/cart/checkout"

    for _ in range(n_requests):
        payload = {
            "items": [
                {"tipo": "voo", "id": "LA3000", "detalhes": "SP-RJ", "preco": 450.0},
                {"tipo": "hotel", "id": "HTL001", "detalhes": "Copacabana Palace", "preco": 800.0},
                {"tipo": "pacote", "id": "PKG001", "detalhes": "Pacote Completo", "preco": 1200.0}
            ]
        }

        start = time.time()
        try:
            response = requests.post(url, json=payload, timeout=10)
            elapsed = time.time() - start

            if response.status_code == 200:
                result = response.json()
                if result.get('sucesso'):
                    times.append(elapsed * 1000)
        except Exception as e:
            print(f"Erro REST: {e}")
            continue

    return times

def test_grpc_bidirectional(n_requests=3):
    if not voos_service_pb2 or not voos_service_pb2_grpc:
        return []

    times = []

    for i in range(n_requests):
        start = time.time()
        messages_received = 0

        try:
            with grpc.insecure_channel('localhost:50051') as channel:
                stub = voos_service_pb2_grpc.VoosServiceStub(channel)

                def message_generator():
                    perguntas = [
                        "Olá, preciso de ajuda com voos",
                        "Quais voos disponíveis para Rio?",
                        "Obrigado!"
                    ]

                    for pergunta in perguntas:
                        yield voos_service_pb2.ChatMessage(
                            usuario="cliente",
                            mensagem=pergunta,
                            timestamp=str(int(time.time())),
                            contexto="voo"
                        )
                        time.sleep(0.05)  

                for resposta in stub.ChatSuporte(message_generator()):
                    messages_received += 1
                    if messages_received >= 3:
                        break

                if messages_received > 0:
                    elapsed = time.time() - start
                    times.append(elapsed * 1000)

        except grpc.RpcError as e:
            print(f"Erro gRPC Bidirectional [{i}]: {e.code()} - {e.details()}")
            continue
        except Exception as e:
            print(f"Erro gRPC Bidirectional geral [{i}]: {e}")
            continue

    return times

def test_rest_bidirectional(n_requests=3):
    try:
        from websocket import create_connection
    except ImportError:
        print("⚠️  websocket-client não instalado. Execute: pip install websocket-client")
        return []

    times = []

    for _ in range(n_requests):
        start = time.time()
        messages_sent = 0
        messages_received = 0

        try:
            ws = create_connection("ws://localhost:3000/chat")

            perguntas = [
                "Olá, preciso de ajuda com voos",
                "Quais são as opções de voo para Rio?",
                "Obrigado pela ajuda!"
            ]

            for pergunta in perguntas:
                ws.send(json.dumps({
                    "remetente": "cliente",
                    "mensagem": pergunta,
                    "timestamp": str(int(time.time()))
                }))
                messages_sent += 1
                time.sleep(0.1)

                result = ws.recv()
                if result:
                    messages_received += 1

            ws.close()
            elapsed = time.time() - start
            times.append(elapsed * 1000)

        except Exception as e:
            print(f"Erro WebSocket: {e}")
            continue

    return times

def test_grpc_alto_volume(n_requests=100):
    return test_grpc_voos_simples(n_requests)

def test_rest_alto_volume(n_requests=100):
    return test_rest_voos_simples(n_requests)

def calcular_estatisticas(times):
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
    
    print(f"CENÁRIO: {nome_cenario}")
    

    print(f"\n{'Métrica':<20} {'gRPC (ms)':<15} {'REST (ms)':<15} {'Diferença (%)':<15}")
    

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
    
    print("COMPARATIVO DE PERFORMANCE: gRPC vs REST")
    print("Demonstração dos 4 Tipos de Comunicação gRPC")

    print("\nCertifique-se de que os seguintes serviços estão rodando:")
    print("  - Servidor gRPC de Voos (porta 50051)")
    print("  - Servidor gRPC de Hotéis (porta 50052)")
    print("  - API Gateway REST (porta 3000)")
    

    input("\nPressione ENTER para iniciar os testes...")

    print("\n\nCenário 1: UNARY RPC - Requisição Simples (10 requisições)...")
    print("   Tipo: Request → Response (1:1)")
    grpc_times_1 = test_grpc_voos_simples(10)
    rest_times_1 = test_rest_voos_simples(10)
    exibir_resultados(
        "UNARY RPC - Consultar Voos Simples",
        calcular_estatisticas(grpc_times_1),
        calcular_estatisticas(rest_times_1)
    )

    print("\n\nCenário 2: UNARY RPC - Requisição Complexa (10 requisições)...")
    print("   Tipo: Request → Response com múltiplos filtros")
    grpc_times_2 = test_grpc_voos_complexo(10)
    rest_times_2 = test_rest_voos_complexo(10)
    exibir_resultados(
        "UNARY RPC - Consultar Voos com Filtros",
        calcular_estatisticas(grpc_times_2),
        calcular_estatisticas(rest_times_2)
    )

    print("\n\nCenário 3: SERVER STREAMING RPC - Monitoramento de Voo (5 requisições)...")
    print("   Tipo: 1 Request → N Responses (stream de updates)")
    grpc_times_3 = test_grpc_server_streaming(5)
    rest_times_3 = test_rest_server_streaming(5)
    exibir_resultados(
        "SERVER STREAMING - Monitorar Status de Voo",
        calcular_estatisticas(grpc_times_3),
        calcular_estatisticas(rest_times_3)
    )

    print("\n\nCenário 4: CLIENT STREAMING RPC - Finalizar Compra (5 requisições)...")
    print("   Tipo: N Requests → 1 Response (envio de múltiplos itens)")
    grpc_times_4 = test_grpc_client_streaming(5)
    rest_times_4 = test_rest_client_streaming(5)
    if grpc_times_4 or rest_times_4:
        exibir_resultados(
            "CLIENT STREAMING - Carrinho de Compras",
            calcular_estatisticas(grpc_times_4),
            calcular_estatisticas(rest_times_4)
        )
    else:
        print("Teste ignorado - serviço de hotel indisponível")

    print("\n\nCenário 5: BIDIRECTIONAL STREAMING RPC - Chat de Suporte (3 requisições)...")
    print("   Tipo: N Requests ↔ N Responses (conversação em tempo real)")
    grpc_times_5 = test_grpc_bidirectional(3)
    rest_times_5 = test_rest_bidirectional(3)
    if grpc_times_5 or rest_times_5:
        exibir_resultados(
            "BIDIRECTIONAL STREAMING - Chat em Tempo Real",
            calcular_estatisticas(grpc_times_5),
            calcular_estatisticas(rest_times_5)
        )
    else:
        print("Teste ignorado - serviço de chat indisponível")

    print("\n\nCenário 6: ALTO VOLUME - Unary RPC (100 requisições)...")
    print("   Tipo: Teste de stress com requisições Unary")
    grpc_times_6 = test_grpc_alto_volume(100)
    rest_times_6 = test_rest_alto_volume(100)
    exibir_resultados(
        "ALTO VOLUME - Stress Test",
        calcular_estatisticas(grpc_times_6),
        calcular_estatisticas(rest_times_6)
    )

if __name__ == '__main__':
    main()
