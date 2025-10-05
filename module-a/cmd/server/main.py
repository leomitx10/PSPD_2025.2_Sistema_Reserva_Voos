import grpc
from concurrent import futures
import time
import random
from datetime import datetime, timedelta
import sys
import os

# Adicionar path dos protos
proto_path = os.path.join(os.path.dirname(__file__), '../../proto')
sys.path.insert(0, proto_path)

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
        classes = ["Econômica", "Executiva", "Primeira Classe"]

        voos = []

        # GARANTIR MUITOS voos nos próximos 10 dias (50-80 por dia para dificultar busca)
        for dia in range(10):
            for _ in range(random.randint(50, 80)):
                origem = random.choice(cidades)
                destino = random.choice([c for c in cidades if c != origem])

                data_base = datetime.now() + timedelta(days=dia)
                horario_partida = data_base.replace(
                    hour=random.randint(6, 22),
                    minute=random.choice([0, 15, 30, 45]),
                    second=0,
                    microsecond=0
                )
                duracao = random.randint(60, 480)
                horario_chegada = horario_partida + timedelta(minutes=duracao)

                classe = random.choice(classes)
                # Preço varia por classe
                preco_base = random.uniform(150.0, 800.0)
                multiplicador = {"Econômica": 1.0, "Executiva": 2.5, "Primeira Classe": 4.0}
                preco = round(preco_base * multiplicador[classe], 2)

                voo = voos_service_pb2.Voo(
                    id=f"V{len(voos)+1:04d}",
                    origem=origem,
                    destino=destino,
                    data=data_base.strftime("%Y-%m-%d"),
                    horario_partida=horario_partida.strftime("%H:%M"),
                    horario_chegada=horario_chegada.strftime("%H:%M"),
                    preco=preco,
                    companhia_aerea=random.choice(companhias),
                    numero_voo=f"{random.choice(['LA', 'G3', 'AD', 'JJ'])}{random.randint(1000, 9999)}",
                    assentos_disponiveis=random.randint(5, 180),  # Sempre com assentos
                    status="ativo",  # Garantir ativo nos próximos 10 dias
                    classe_economica=classe,
                    aeronave=random.choice(aeronaves),
                    duracao_minutos=duracao
                )
                voos.append(voo)

        # Gerar voos restantes (até 5000 total) para período futuro
        while len(voos) < 5000:
            origem = random.choice(cidades)
            destino = random.choice([c for c in cidades if c != origem])

            data_base = datetime.now() + timedelta(days=random.randint(11, 60))
            horario_partida = data_base.replace(
                hour=random.randint(6, 22),
                minute=random.choice([0, 15, 30, 45]),
                second=0,
                microsecond=0
            )
            duracao = random.randint(60, 480)
            horario_chegada = horario_partida + timedelta(minutes=duracao)

            classe = random.choice(classes)
            preco_base = random.uniform(150.0, 800.0)
            multiplicador = {"Econômica": 1.0, "Executiva": 2.5, "Primeira Classe": 4.0}
            preco = round(preco_base * multiplicador[classe], 2)

            voo = voos_service_pb2.Voo(
                id=f"V{len(voos)+1:04d}",
                origem=origem,
                destino=destino,
                data=data_base.strftime("%Y-%m-%d"),
                horario_partida=horario_partida.strftime("%H:%M"),
                horario_chegada=horario_chegada.strftime("%H:%M"),
                preco=preco,
                companhia_aerea=random.choice(companhias),
                numero_voo=f"{random.choice(['LA', 'G3', 'AD', 'JJ'])}{random.randint(1000, 9999)}",
                assentos_disponiveis=random.randint(0, 180),
                status=random.choice(["ativo", "ativo", "ativo", "cancelado", "lotado"]),
                classe_economica=classe,
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

    def MonitorarVoo(self, request, context):
        """
        Server Streaming RPC - Monitora status de um voo em tempo real
        Envia atualizações contínuas do status do voo
        """
        numero_voo = request.numero_voo
        print(f"[MONITORAR VOO] Iniciando monitoramento do voo {numero_voo}")

        # Simula diferentes status do voo
        status_timeline = [
            {"status": "aguardando_embarque", "mensagem": f"Voo {numero_voo} aguardando no portão de embarque", "progresso": 10},
            {"status": "embarcando", "mensagem": f"Embarque do voo {numero_voo} iniciado", "progresso": 30},
            {"status": "pronto_decolagem", "mensagem": f"Voo {numero_voo} pronto para decolagem", "progresso": 50},
            {"status": "decolou", "mensagem": f"Voo {numero_voo} decolou com sucesso", "progresso": 60},
            {"status": "em_voo", "mensagem": f"Voo {numero_voo} em cruzeiro a 35.000 pés", "progresso": 80},
            {"status": "pousou", "mensagem": f"Voo {numero_voo} pousou no destino", "progresso": 95},
            {"status": "finalizado", "mensagem": f"Voo {numero_voo} finalizado - passageiros desembarcando", "progresso": 100}
        ]

        for update in status_timeline:
            time.sleep(2)  # Simula intervalo entre atualizações

            yield voos_service_pb2.StatusVooUpdate(
                numero_voo=numero_voo,
                status=update["status"],
                mensagem=update["mensagem"],
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                progresso_percentual=update["progresso"]
            )

            print(f"[MONITORAR VOO] {update['mensagem']} ({update['progresso']}%)")

    def ChatSuporte(self, request_iterator, context):
        """
        Bidirectional Streaming RPC - Chat de suporte em tempo real
        Responde apenas mensagens relacionadas a voos
        """
        print("[CHAT SUPORTE VOOS] Chat iniciado")

        for mensagem_cliente in request_iterator:
            print(f"[CHAT VOOS] Recebido: {mensagem_cliente.mensagem}")

            # Detecta se a mensagem é sobre voos, pacotes ou geral
            palavras_voo = ["voo", "voos", "voar", "aereo", "aéreo", "aviao", "avião", "passagem", "passagens"]
            palavras_pacote = ["pacote", "pacotes", "combo"]
            mensagem_lower = mensagem_cliente.mensagem.lower()
            contexto = mensagem_cliente.contexto if hasattr(mensagem_cliente, 'contexto') else ""

            # Responde se for sobre voos, pacotes OU mensagem geral (sem palavra-chave específica)
            is_about_flight = any(palavra in mensagem_lower for palavra in palavras_voo)
            is_about_package = any(palavra in mensagem_lower for palavra in palavras_pacote)
            is_general = contexto == "geral" or (not is_about_flight and not is_about_package and contexto != "hotel")

            if is_about_flight or is_about_package or is_general:
                time.sleep(0.5)  # Simula tempo de processamento

                # Gera resposta contextual
                if is_about_package:
                    resposta = "✈️ VOOS - Nossos pacotes incluem passagens aéreas com LATAM, GOL, Azul e mais! Voos a partir de R$ 150."
                elif is_general:
                    resposta = "✈️ VOOS - Posso te ajudar com informações sobre voos! Trabalhamos com as melhores companhias aéreas."
                elif "preco" in mensagem_lower or "preço" in mensagem_lower or "barato" in mensagem_lower:
                    resposta = "📊 Temos voos a partir de R$ 150! Use os filtros de preço para encontrar as melhores ofertas."
                elif "horario" in mensagem_lower or "horário" in mensagem_lower:
                    resposta = "🕐 Oferecemos voos em diversos horários: manhã (6h-12h), tarde (12h-18h) e noite (18h-0h)."
                elif "companhia" in mensagem_lower:
                    resposta = "✈️ Trabalhamos com LATAM, GOL, Azul, TAM e Avianca. Você tem preferência?"
                elif "classe" in mensagem_lower:
                    resposta = "🎫 Temos 3 classes disponíveis: Econômica, Executiva e Primeira Classe."
                elif "monitorar" in mensagem_lower:
                    resposta = "📡 Use o botão 'Monitorar Voo' no canto inferior direito para acompanhar seu voo em tempo real!"
                else:
                    resposta = f"✈️ Olá! Como posso ajudar com informações sobre voos? Temos diversas opções disponíveis."

                yield voos_service_pb2.ChatMessage(
                    usuario="suporte",
                    mensagem=resposta,
                    timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    contexto="voo"
                )

                print(f"[CHAT VOOS] Respondido: {resposta}")
            else:
                # Não responde se não for sobre voos (deixa para o módulo de hotéis responder)
                print(f"[CHAT VOOS] Mensagem não é sobre voos, ignorando...")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    voos_service_pb2_grpc.add_VoosServiceServicer_to_server(VoosServiceImpl(), server)

    # Usar 0.0.0.0 para aceitar conexões de qualquer interface (necessário no Docker)
    server.add_insecure_port('0.0.0.0:50051')
    server.start()
    print("=" * 60)
    print("Servidor gRPC de Voos rodando na porta 50051")
    print("Pressione Ctrl+C para parar")
    print("=" * 60)
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
