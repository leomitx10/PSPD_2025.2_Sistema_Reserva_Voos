import grpc
from concurrent import futures
import time
import random
from datetime import datetime, timedelta
import voos_service_pb2
import voos_service_pb2_grpc

class VoosServiceImpl(voos_service_pb2_grpc.VoosServiceServicer):
    def __init__(self):
        self.voos_database = self._gerar_base_voos()
    
    def _gerar_base_voos(self):
        """Gera uma base de dados simulada de voos"""
        companhias = ["LATAM", "GOL", "Azul", "TAM", "Avianca"]
        cidades = ["São Paulo", "Rio de Janeiro", "Brasília", "Belo Horizonte", 
                  "Salvador", "Recife", "Fortaleza", "Manaus", "Porto Alegre"]
        aeronaves = ["Boeing 737", "Airbus A320", "Embraer E190", "Boeing 777"]
        
        voos = []
        for i in range(1000):  
            origem = random.choice(cidades)
            destino = random.choice([c for c in cidades if c != origem])
            
            data_base = datetime.now() + timedelta(days=random.randint(1, 30))
            horario_partida = data_base.replace(
                hour=random.randint(6, 22), 
                minute=random.choice([0, 15, 30, 45])
            )
            duracao = random.randint(60, 480)  # 1h a 8h
            horario_chegada = horario_partida + timedelta(minutes=duracao)
            
            voo = voos_service_pb2.Voo(
                id=f"V{i+1:04d}",
                origem=origem,
                destino=destino,
                data=data_base.strftime("%Y-%m-%d"),
                horario_partida=horario_partida.strftime("%H:%M"),
                horario_chegada=horario_chegada.strftime("%H:%M"),
                preco=round(random.uniform(150.0, 1500.0), 2),
                companhia_aerea=random.choice(companhias),
                numero_voo=f"{random.choice(['LA', 'G3', 'AD', 'JJ'])}{random.randint(1000, 9999)}",
                assentos_disponiveis=random.randint(0, 180),
                status=random.choice(["ativo", "ativo", "ativo", "cancelado", "lotado"]),
                classe_economica="Econômica",
                aeronave=random.choice(aeronaves),
                duracao_minutos=duracao
            )
            voos.append(voo)
        
        return voos
    
    def ConsultarVoos(self, request, context):
        inicio_processamento = time.time()
        
        time.sleep(random.uniform(1, 3))
        
        voos_filtrados = self._aplicar_filtros(request)
        
        voos_ordenados = self._ordenar_voos(voos_filtrados, request.ordenacao)
        
        # Comentado: simulação de falha aleatória
        # if random.random() < 0.1:  
        #     voos_ordenados = []
        
        tempo_processamento = time.time() - inicio_processamento
        
        return voos_service_pb2.ConsultaVoosResponse(
            voos=voos_ordenados,
            total_encontrados=len(voos_ordenados),
            tempo_processamento=f"{tempo_processamento:.2f}s"
        )
    
    def _aplicar_filtros(self, request):
        voos_filtrados = self.voos_database.copy()
        
        if request.origem:
            voos_filtrados = [v for v in voos_filtrados if v.origem.lower() == request.origem.lower()]
        
        if request.destino:
            voos_filtrados = [v for v in voos_filtrados if v.destino.lower() == request.destino.lower()]
        
        if request.data:
            voos_filtrados = [v for v in voos_filtrados if v.data == request.data]

        if request.preco_max > 0:
            voos_filtrados = [v for v in voos_filtrados if v.preco <= request.preco_max]

        if request.companhia_aerea:
            voos_filtrados = [v for v in voos_filtrados 
                            if v.companhia_aerea.lower() == request.companhia_aerea.lower()]

        if request.faixa_horario:
            voos_filtrados = self._filtrar_por_horario(voos_filtrados, request.faixa_horario)

        voos_filtrados = [v for v in voos_filtrados 
                         if v.status == "ativo" and v.assentos_disponiveis > 0]
        
        return voos_filtrados
    
    def _filtrar_por_horario(self, voos, faixa_horario):
        if faixa_horario == "manha":
            return [v for v in voos if "06:00" <= v.horario_partida < "12:00"]
        elif faixa_horario == "tarde":
            return [v for v in voos if "12:00" <= v.horario_partida < "18:00"]
        elif faixa_horario == "noite":
            return [v for v in voos if "18:00" <= v.horario_partida <= "23:59"]
        return voos
    
    def _ordenar_voos(self, voos, criterio_ordenacao):
        if criterio_ordenacao == "preco":
            return sorted(voos, key=lambda v: v.preco)
        elif criterio_ordenacao == "horario":
            return sorted(voos, key=lambda v: v.horario_partida)
        elif criterio_ordenacao == "duracao":
            return sorted(voos, key=lambda v: v.duracao_minutos)
        else:  
            return sorted(voos, key=lambda v: v.preco)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    voos_service_pb2_grpc.add_VoosServiceServicer_to_server(VoosServiceImpl(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Servidor iniciado na porta 50051")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
