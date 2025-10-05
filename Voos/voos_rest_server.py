from flask import Flask, request, jsonify
from flask_cors import CORS
import time
import random
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

class VoosDatabase:
    def __init__(self):
        self.voos = self._gerar_base_voos()

    def _gerar_base_voos(self):
        """Gera uma base de dados simulada de voos (mesma do gRPC)"""
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
            duracao = random.randint(60, 480)
            horario_chegada = horario_partida + timedelta(minutes=duracao)

            voo = {
                "id": f"V{i+1:04d}",
                "origem": origem,
                "destino": destino,
                "data": data_base.strftime("%Y-%m-%d"),
                "horario_partida": horario_partida.strftime("%H:%M"),
                "horario_chegada": horario_chegada.strftime("%H:%M"),
                "preco": round(random.uniform(150.0, 1500.0), 2),
                "companhia_aerea": random.choice(companhias),
                "numero_voo": f"{random.choice(['LA', 'G3', 'AD', 'JJ'])}{random.randint(1000, 9999)}",
                "assentos_disponiveis": random.randint(0, 180),
                "status": random.choice(["ativo", "ativo", "ativo", "cancelado", "lotado"]),
                "classe_economica": "Econômica",
                "aeronave": random.choice(aeronaves),
                "duracao_minutos": duracao
            }
            voos.append(voo)

        return voos

    def buscar_voos(self, filtros):
        """Aplica filtros aos voos"""
        inicio = time.time()
        time.sleep(random.uniform(1, 3))  # Simula processamento

        voos_filtrados = self.voos.copy()

        if filtros.get('origem'):
            voos_filtrados = [v for v in voos_filtrados
                            if v['origem'].lower() == filtros['origem'].lower()]

        if filtros.get('destino'):
            voos_filtrados = [v for v in voos_filtrados
                            if v['destino'].lower() == filtros['destino'].lower()]

        if filtros.get('data'):
            voos_filtrados = [v for v in voos_filtrados if v['data'] == filtros['data']]

        if filtros.get('preco_max', 0) > 0:
            voos_filtrados = [v for v in voos_filtrados
                            if v['preco'] <= filtros['preco_max']]

        if filtros.get('companhia_aerea'):
            voos_filtrados = [v for v in voos_filtrados
                            if v['companhia_aerea'].lower() == filtros['companhia_aerea'].lower()]

        if filtros.get('faixa_horario'):
            voos_filtrados = self._filtrar_por_horario(voos_filtrados, filtros['faixa_horario'])

        # Filtrar apenas ativos com assentos
        voos_filtrados = [v for v in voos_filtrados
                         if v['status'] == 'ativo' and v['assentos_disponiveis'] > 0]

        # Ordenar
        criterio = filtros.get('ordenacao', 'preco')
        if criterio == 'preco':
            voos_filtrados.sort(key=lambda v: v['preco'])
        elif criterio == 'horario':
            voos_filtrados.sort(key=lambda v: v['horario_partida'])
        elif criterio == 'duracao':
            voos_filtrados.sort(key=lambda v: v['duracao_minutos'])

        tempo_processamento = time.time() - inicio

        return {
            'voos': voos_filtrados,
            'total_encontrados': len(voos_filtrados),
            'tempo_processamento': f"{tempo_processamento:.2f}s"
        }

    def _filtrar_por_horario(self, voos, faixa):
        if faixa == "manha":
            return [v for v in voos if "06:00" <= v['horario_partida'] < "12:00"]
        elif faixa == "tarde":
            return [v for v in voos if "12:00" <= v['horario_partida'] < "18:00"]
        elif faixa == "noite":
            return [v for v in voos if "18:00" <= v['horario_partida'] <= "23:59"]
        return voos

db = VoosDatabase()

@app.route('/voos/search', methods=['POST'])
def buscar_voos():
    """Endpoint REST para buscar voos"""
    filtros = request.json or {}
    resultado = db.buscar_voos(filtros)
    return jsonify(resultado)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "OK", "service": "Voos REST"})

if __name__ == '__main__':
    print("=" * 60)
    print("Servidor REST de Voos rodando na porta 5001")
    print("Para comparação de performance com gRPC")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5001, debug=False)
