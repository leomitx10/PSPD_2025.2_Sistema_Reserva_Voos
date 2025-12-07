"""
Cenários de Teste de Carga
Define diferentes configurações de teste para avaliar o sistema
Tempo total estimado: ~5 minutos
"""

SCENARIOS = {
    "cenario_1_baseline": {
        "description": "Baseline - Configuração mínima",
        "users": 10,
        "spawn_rate": 5,
        "duration": "5m",
        "k8s_config": {
            "voos_replicas": 2,
            "hoteis_replicas": 2,
            "gateway_replicas": 2,
            "hpa_enabled": False
        },
        "objetivo": "Estabelecer baseline de performance sem autoscaling"
    },

    "cenario_2_moderate": {
        "description": "Carga Moderada - HPA habilitado",
        "users": 30,
        "spawn_rate": 10,
        "duration": "5m",
        "k8s_config": {
            "voos_replicas": 2,
            "hoteis_replicas": 2,
            "gateway_replicas": 2,
            "hpa_enabled": True,
            "hpa_max_replicas": 10
        },
        "objetivo": "Avaliar comportamento do HPA com carga moderada"
    },

    "cenario_3_high_load": {
        "description": "Alta Carga - Teste de escalabilidade",
        "users": 50,
        "spawn_rate": 10,
        "duration": "5m",
        "k8s_config": {
            "voos_replicas": 3,
            "hoteis_replicas": 3,
            "gateway_replicas": 3,
            "hpa_enabled": True,
            "hpa_max_replicas": 15
        },
        "objetivo": "Testar limites de escalabilidade horizontal"
    },

    "cenario_4_spike": {
        "description": "Spike Test - Pico súbito de requisições",
        "users": 100,
        "spawn_rate": 50,  # Crescimento muito rápido
        "duration": "5m",
        "k8s_config": {
            "voos_replicas": 2,
            "hoteis_replicas": 2,
            "gateway_replicas": 2,
            "hpa_enabled": True,
            "hpa_max_replicas": 15
        },
        "objetivo": "Avaliar resposta a picos súbitos de tráfego"
    },

    "cenario_5_stress": {
        "description": "Teste de Estresse - Identificar breaking point",
        "users": 150,
        "spawn_rate": 30,
        "duration": "5m",
        "k8s_config": {
            "voos_replicas": 2,
            "hoteis_replicas": 2,
            "gateway_replicas": 2,
            "hpa_enabled": True,
            "hpa_max_replicas": 20
        },
        "objetivo": "Identificar ponto de quebra do sistema"
    }
}


def print_scenario_info(scenario_name):
    """Imprime informações de um cenário"""
    if scenario_name not in SCENARIOS:
        print(f"Cenário '{scenario_name}' não encontrado!")
        return

    scenario = SCENARIOS[scenario_name]
    print("=" * 80)
    print(f"CENÁRIO: {scenario_name}")
    print("=" * 80)
    print(f"Descrição: {scenario['description']}")
    print(f"Objetivo: {scenario['objetivo']}")
    print(f"\nConfiguração de Carga:")
    print(f"  - Usuários simultâneos: {scenario['users']}")
    print(f"  - Taxa de spawn: {scenario['spawn_rate']} usuários/segundo")
    print(f"  - Duração: {scenario['duration']}")
    print(f"\nConfiguração Kubernetes:")
    for key, value in scenario['k8s_config'].items():
        print(f"  - {key}: {value}")
    print("=" * 80)


def get_locust_command(scenario_name, host):
    """Gera comando Locust para o cenário"""
    if scenario_name not in SCENARIOS:
        return None

    scenario = SCENARIOS[scenario_name]

    cmd = f"locust -f locustfile.py "
    cmd += f"--host={host} "
    cmd += f"--users={scenario['users']} "
    cmd += f"--spawn-rate={scenario['spawn_rate']} "
    cmd += f"--run-time={scenario['duration']} "
    cmd += f"--headless "
    cmd += f"--only-summary "
    cmd += f"--html=results/{scenario_name}_report.html "
    cmd += f"--csv=results/{scenario_name}"

    return cmd


if __name__ == "__main__":
    print("Cenários de Teste Disponíveis:\n")
    for name, scenario in SCENARIOS.items():
        print(f"{name}:")
        print(f"  {scenario['description']}")
        print(f"  Usuários: {scenario['users']}, Duração: {scenario['duration']}")
        print()
