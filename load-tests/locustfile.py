"""
Locust Load Testing - Sistema de Reserva de Voos
Testes de carga para avaliar performance do sistema distribuído
"""

from locust import HttpUser, task, between, events
import random
import json
import time
from datetime import datetime

# Dados de exemplo para testes
ORIGINS = ["GRU", "CGH", "BSB", "RIO", "POA", "FOR", "SSA", "VCP", "GIG", "SDU"]
DESTINATIONS = ["GRU", "CGH", "BSB", "RIO", "POA", "FOR", "SSA", "VCP", "GIG", "SDU"]
CITIES = ["São Paulo", "Brasília", "Rio de Janeiro", "Belo Horizonte", "Salvador",
          "Fortaleza", "Recife", "Porto Alegre", "Curitiba", "Manaus"]


class ReservasUser(HttpUser):
    """
    Usuário simulado do sistema de reservas.
    Simula comportamento real de usuários navegando e fazendo reservas.
    """

    # Tempo de espera entre tarefas (simula tempo de leitura/decisão do usuário)
    wait_time = between(1, 3)

    def on_start(self):
        """Executado quando o usuário inicia"""
        self.client.verify = False  # Desabilita verificação SSL para testes
        print(f"[{datetime.now()}] Novo usuário iniciado")

    @task(5)
    def buscar_voos(self):
        """
        Busca voos disponíveis.
        Task weight = 5 (executada 5x mais que outras com weight 1)
        """
        origem = random.choice(ORIGINS)
        destino = random.choice([d for d in DESTINATIONS if d != origem])

        with self.client.get(
            f"/flights?origin={origem}&destination={destino}",
            catch_response=True,
            name="/flights [Busca Voos]"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status {response.status_code}")

    @task(4)
    def buscar_hoteis(self):
        """
        Busca hotéis disponíveis.
        Task weight = 4
        """
        cidade = random.choice(CITIES)

        with self.client.get(
            f"/hotels?city={cidade}",
            catch_response=True,
            name="/hotels [Busca Hotéis]"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status {response.status_code}")

    @task(3)
    def buscar_pacotes(self):
        """
        Busca pacotes (voo + hotel).
        Task weight = 3
        """
        origem = random.choice(ORIGINS)
        destino = random.choice([d for d in DESTINATIONS if d != origem])
        cidade = random.choice(CITIES)

        with self.client.get(
            f"/packages?origin={origem}&destination={destino}&city={cidade}",
            catch_response=True,
            name="/packages [Busca Pacotes]"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status {response.status_code}")

    @task(2)
    def health_check(self):
        """
        Verifica saúde da aplicação.
        Task weight = 2
        """
        with self.client.get(
            "/health",
            catch_response=True,
            name="/health [Health Check]"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status {response.status_code}")

    @task(1)
    def realizar_compra(self):
        """
        Simula finalização de compra.
        Task weight = 1 (menos frequente - comportamento real)
        """
        # Simula seleção de itens
        items = {
            "flight_id": f"FL{random.randint(100, 999)}",
            "hotel_id": f"HT{random.randint(100, 999)}",
            "passengers": random.randint(1, 4)
        }

        with self.client.post(
            "/checkout",
            json=items,
            catch_response=True,
            name="/checkout [Finalizar Compra]"
        ) as response:
            if response.status_code in [200, 201]:
                response.success()
            else:
                response.failure(f"Status {response.status_code}")


class StressTestUser(HttpUser):
    """
    Usuário para testes de estresse.
    Executa requisições mais agressivas sem tempo de espera.
    """

    wait_time = between(0.1, 0.5)  # Espera muito menor

    @task(10)
    def buscar_voos_stress(self):
        """Busca voos em modo estresse"""
        origem = random.choice(ORIGINS)
        destino = random.choice([d for d in DESTINATIONS if d != origem])
        self.client.get(f"/flights?origin={origem}&destination={destino}")

    @task(5)
    def buscar_hoteis_stress(self):
        """Busca hotéis em modo estresse"""
        cidade = random.choice(CITIES)
        self.client.get(f"/hotels?city={cidade}")


# Eventos customizados para métricas adicionais
@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, **kwargs):
    """
    Callback executado a cada requisição.
    Útil para métricas customizadas.
    """
    if exception:
        print(f"[ERRO] {name}: {exception}")
    elif response_time > 2000:  # Alerta para requisições > 2s
        print(f"[LENTO] {name}: {response_time}ms")


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Executado no início do teste"""
    print("=" * 80)
    print(f"Iniciando teste de carga - {datetime.now()}")
    print(f"Host: {environment.host}")
    print("=" * 80)


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Executado no final do teste"""
    print("=" * 80)
    print(f"Teste finalizado - {datetime.now()}")
    print("Verifique as métricas no Prometheus e Locust Web UI")
    print("=" * 80)
