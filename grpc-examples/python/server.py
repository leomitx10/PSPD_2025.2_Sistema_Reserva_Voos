import grpc
from concurrent import futures
import time
from datetime import datetime
import examples_pb2
import examples_pb2_grpc

class GrpcExamplesServicer(examples_pb2_grpc.GrpcExamplesServiceServicer):
    def UnaryCall(self, request, context):
        print(f"[UNARY] Recebida mensagem: {request.message}")
        return examples_pb2.UnaryResponse(
            reply=f"Processado: {request.message}",
            timestamp=datetime.now().isoformat()
        )

    def ServerStreamingCall(self, request, context):
        print(f"[SERVER STREAMING] Enviando {request.count} mensagens com prefixo '{request.prefix}'")
        for i in range(request.count):
            time.sleep(0.5)  
            yield examples_pb2.ServerStreamingResponse(
                sequence=i + 1,
                message=f"{request.prefix} - Mensagem {i + 1}/{request.count}"
            )

    def ClientStreamingCall(self, request_iterator, context):
        received_count = 0
        all_data = []

        for request in request_iterator:
            received_count += 1
            all_data.append(request.data)
            print(f"[CLIENT STREAMING] Recebido #{received_count}: {request.data}")

        summary = f"Total de {received_count} mensagens processadas. Dados: {', '.join(all_data[:5])}..."
        return examples_pb2.ClientStreamingResponse(
            total_received=received_count,
            summary=summary
        )

    def BidirectionalStreamingCall(self, request_iterator, context):
        for request in request_iterator:
            print(f"[BIDIRECTIONAL] Recebido: {request.message}")
            yield examples_pb2.BidirectionalResponse(
                echo=f"Echo: {request.message.upper()}",
                processed_at=datetime.now().isoformat()
            )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    examples_pb2_grpc.add_GrpcExamplesServiceServicer_to_server(
        GrpcExamplesServicer(), server
    )
    server.add_insecure_port('[::]:50053')
    server.start()
    print("Servidor gRPC Examples rodando na porta 50053")
    print("Demonstração dos 4 tipos de comunicação gRPC")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
