import grpc
import sys
import os
from datetime import datetime, timedelta

proto_path = os.path.join(os.path.dirname(__file__), '../../proto')
sys.path.insert(0, proto_path)

import voos_service_pb2
import voos_service_pb2_grpc

class VoosClient:
    def __init__(self, host='localhost', port=50051):
        self.channel = grpc.insecure_channel(f'{host}:{port}')
        self.stub = voos_service_pb2_grpc.VoosServiceStub(self.channel)
    
    def consultar_voos(self, origem=None, destino=None, data=None, 
                      preco_max=0, companhia_aerea=None, faixa_horario=None, 
                      ordenacao="preco"):
        request = voos_service_pb2.ConsultaVoosRequest(
            origem=origem or "",
            destino=destino or "",
            data=data or "",
            preco_max=preco_max,
            companhia_aerea=companhia_aerea or "",
            faixa_horario=faixa_horario or "",
            ordenacao=ordenacao
        )
        
        try:
            response = self.stub.ConsultarVoos(request)
            return response
        except grpc.RpcError as e:
            print(f"Erro: {e}")
            return None
    
    def close(self):
        self.channel.close()

def teste_carga():
    import threading
    import time
    
    def fazer_consultas(cliente_id):
        client = VoosClient()
        for i in range(10):
            print(f"Cliente {cliente_id} - Consulta {i+1}")
            response = client.consultar_voos(
                origem="São Paulo",
                destino="Rio de Janeiro",
                data=(datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
            )
            if response:
                print(f"Cliente {cliente_id} - Encontrados: {response.total_encontrados} voos")
            time.sleep(0.5)
        client.close()
    
    threads = []
    for i in range(5):
        thread = threading.Thread(target=fazer_consultas, args=(i+1,))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()

if __name__ == '__main__':
    client = VoosClient()
    
    print("=" * 60)
    print("TESTE 1: Consulta sem filtros (todos os voos)")
    print("=" * 60)
    response = client.consultar_voos()
    
    if response:
        print(f"Voos encontrados: {response.total_encontrados}")
        print(f"Tempo de processamento: {response.tempo_processamento}")
        for i, voo in enumerate(response.voos[:3]): 
            print(f"\n{i+1}. {voo.companhia_aerea} {voo.numero_voo}")
            print(f"   {voo.origem} → {voo.destino}")
            print(f"   {voo.data} {voo.horario_partida} - {voo.horario_chegada}")
            print(f"   R$ {voo.preco:.2f} | {voo.assentos_disponiveis} assentos")
    
    print("\n" + "=" * 60)
    print("TESTE 2: Consulta apenas por origem (São Paulo)")
    print("=" * 60)
    response = client.consultar_voos(origem="São Paulo")
    
    if response:
        print(f"Voos encontrados: {response.total_encontrados}")
        print(f"Tempo de processamento: {response.tempo_processamento}")
        for i, voo in enumerate(response.voos[:3]): 
            print(f"\n{i+1}. {voo.companhia_aerea} {voo.numero_voo}")
            print(f"   {voo.origem} → {voo.destino}")
            print(f"   {voo.data} {voo.horario_partida} - {voo.horario_chegada}")
            print(f"   R$ {voo.preco:.2f} | {voo.assentos_disponiveis} assentos")
    
    print("\n" + "=" * 60)
    print("TESTE 3: Consulta por hoje")
    print("=" * 60)
    hoje = datetime.now().strftime("%Y-%m-%d")
    response = client.consultar_voos(data=hoje)
    
    if response:
        print(f"Voos encontrados para hoje ({hoje}): {response.total_encontrados}")
        print(f"Tempo de processamento: {response.tempo_processamento}")
        for i, voo in enumerate(response.voos[:3]):  
            print(f"\n{i+1}. {voo.companhia_aerea} {voo.numero_voo}")
            print(f"   {voo.origem} → {voo.destino}")
            print(f"   {voo.data} {voo.horario_partida} - {voo.horario_chegada}")
            print(f"   R$ {voo.preco:.2f} | {voo.assentos_disponiveis} assentos")
    
    print("\n" + "=" * 60)
    print("TESTE 4: Consulta por preço máximo (R$ 300)")
    print("=" * 60)
    response = client.consultar_voos(preco_max=300)
    
    if response:
        print(f"Voos encontrados até R$ 300: {response.total_encontrados}")
        print(f"Tempo de processamento: {response.tempo_processamento}")
        for i, voo in enumerate(response.voos[:3]):  
            print(f"\n{i+1}. {voo.companhia_aerea} {voo.numero_voo}")
            print(f"   {voo.origem} → {voo.destino}")
            print(f"   {voo.data} {voo.horario_partida} - {voo.horario_chegada}")
            print(f"   R$ {voo.preco:.2f} | {voo.assentos_disponiveis} assentos")
    
    client.close()
