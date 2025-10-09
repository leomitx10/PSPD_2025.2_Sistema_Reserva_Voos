import grpc
import time
import examples_pb2
import examples_pb2_grpc

def test_unary_call(stub):
    print("\n1. UNARY CALL - Requisição/Resposta Simples")

    request = examples_pb2.UnaryRequest(message="Olá, servidor!")
    response = stub.UnaryCall(request)

    print(f"Enviado: {request.message}")
    print(f"Recebido: {response.reply}")
    print(f"Timestamp: {response.timestamp}")

def test_server_streaming(stub):
    print("\n2. SERVER STREAMING - Servidor envia stream")

    request = examples_pb2.ServerStreamingRequest(count=5, prefix="LOG")
    responses = stub.ServerStreamingCall(request)

    print(f"Solicitando {request.count} mensagens...")
    for response in responses:
        print(f"  [{response.sequence}] {response.message}")

def test_client_streaming(stub):
    print("\n3. CLIENT STREAMING - Cliente envia stream")

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
    print("\n4. BIDIRECTIONAL STREAMING - Comunicação bidirecional")

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
    print("\nDEMONSTRAÇÃO DOS 4 TIPOS DE COMUNICAÇÃO gRPC")

    with grpc.insecure_channel('localhost:50053') as channel:
        stub = examples_pb2_grpc.GrpcExamplesServiceStub(channel)

        try:
            test_unary_call(stub)
            test_server_streaming(stub)
            test_client_streaming(stub)
            test_bidirectional_streaming(stub)

        except grpc.RpcError as e:
            print(f"\nErro ao conectar ao servidor: {e.details()}")
            print("Certifique-se de que o servidor está rodando na porta 50053\n")

if __name__ == '__main__':
    run()
