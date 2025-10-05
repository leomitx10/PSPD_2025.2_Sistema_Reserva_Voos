import grpc
import time
import examples_pb2
import examples_pb2_grpc

def test_unary_call(stub):
    """Teste do Unary RPC - Simples requisição/resposta"""
    print("\n" + "=" * 60)
    print("1. UNARY CALL - Requisição/Resposta Simples")
    print("=" * 60)
    print("Caso de uso: Autenticação, consultas simples, validações\n")

    request = examples_pb2.UnaryRequest(message="Olá, servidor!")
    response = stub.UnaryCall(request)

    print(f"Enviado: {request.message}")
    print(f"Recebido: {response.reply}")
    print(f"Timestamp: {response.timestamp}")

def test_server_streaming(stub):
    """Teste do Server Streaming RPC - Servidor envia múltiplas respostas"""
    print("\n" + "=" * 60)
    print("2. SERVER STREAMING - Servidor envia stream")
    print("=" * 60)
    print("Caso de uso: Download de arquivos, logs em tempo real, notificações\n")

    request = examples_pb2.ServerStreamingRequest(count=5, prefix="LOG")
    responses = stub.ServerStreamingCall(request)

    print(f"Solicitando {request.count} mensagens...")
    for response in responses:
        print(f"  [{response.sequence}] {response.message}")

def test_client_streaming(stub):
    """Teste do Client Streaming RPC - Cliente envia múltiplas requisições"""
    print("\n" + "=" * 60)
    print("3. CLIENT STREAMING - Cliente envia stream")
    print("=" * 60)
    print("Caso de uso: Upload de arquivos, envio de métricas, dados em lote\n")

    def generate_requests():
        data_items = ["Dados-1", "Dados-2", "Dados-3", "Dados-4", "Dados-5"]
        for item in data_items:
            print(f"  Enviando: {item}")
            yield examples_pb2.ClientStreamingRequest(data=item)
            time.sleep(0.3)

    response = stub.ClientStreamingCall(generate_requests())
    print(f"\nResposta final do servidor:")
    print(f"  Total recebido: {response.total_received}")
    print(f"  Resumo: {response.summary}")

def test_bidirectional_streaming(stub):
    """Teste do Bidirectional Streaming RPC - Ambos enviam streams"""
    print("\n" + "=" * 60)
    print("4. BIDIRECTIONAL STREAMING - Comunicação bidirecional")
    print("=" * 60)
    print("Caso de uso: Chat em tempo real, jogos multiplayer, sincronização\n")

    def generate_requests():
        messages = ["Olá", "Como vai?", "Tudo bem!", "Até logo"]
        for msg in messages:
            print(f"  Enviando: {msg}")
            yield examples_pb2.BidirectionalRequest(message=msg)
            time.sleep(0.5)

    responses = stub.BidirectionalStreamingCall(generate_requests())

    for response in responses:
        print(f"  Recebido: {response.echo} (em {response.processed_at})")

def run():
    print("\n" + "=" * 60)
    print("DEMONSTRAÇÃO DOS 4 TIPOS DE COMUNICAÇÃO gRPC")
    print("=" * 60)

    with grpc.insecure_channel('localhost:50053') as channel:
        stub = examples_pb2_grpc.GrpcExamplesServiceStub(channel)

        try:
            test_unary_call(stub)
            test_server_streaming(stub)
            test_client_streaming(stub)
            test_bidirectional_streaming(stub)

            print("\n" + "=" * 60)
            print("CONCLUSÃO:")
            print("=" * 60)
            print("""
1. UNARY: Ideal para operações simples e rápidas
2. SERVER STREAMING: Melhor para enviar grandes volumes de dados ao cliente
3. CLIENT STREAMING: Útil para receber dados em lote do cliente
4. BIDIRECTIONAL: Perfeito para comunicação em tempo real bidirecional
            """)

        except grpc.RpcError as e:
            print(f"\nErro ao conectar ao servidor: {e.details()}")
            print("Certifique-se de que o servidor está rodando na porta 50053")

if __name__ == '__main__':
    run()
