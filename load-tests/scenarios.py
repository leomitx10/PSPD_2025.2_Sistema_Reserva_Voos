"""
Cenários de Teste de Carga
Define diferentes configurações de teste para avaliar o sistema
"""

SCENARIOS = {
    "cenario_1_baseline": {
        "description": "Baseline - Configuração mínima",
        "users": 10,
        "spawn_rate": 2,
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
        "users": 50,
        "spawn_rate": 5,
        "duration": "10m",
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
        "users": 200,
        "spawn_rate": 10,
        "duration": "15m",
        "k8s_config": {
            "voos_replicas": 3,
            "hoteis_replicas": 3,
            "gateway_replicas": 3,
            "hpa_enabled": True,
            "hpa_max_replicas": 15
        },
        "objetivo": "Testar limites de escalabilidade horizontal"
    },

    "cenario_4_stress": {
        "description": "Teste de Estresse - Identificar breaking point",
        "users": 500,
        "spawn_rate": 25,
        "duration": "10m",
        "k8s_config": {
            "voos_replicas": 2,
            "hoteis_replicas": 2,
            "gateway_replicas": 2,
            "hpa_enabled": True,
            "hpa_max_replicas": 20
        },
        "objetivo": "Identificar ponto de quebra do sistema"
    },

    "cenario_5_spike": {
        "description": "Spike Test - Pico súbito de requisições",
        "users": 300,
        "spawn_rate": 100,  # Crescimento muito rápido
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

    "cenario_6_sustained": {
        "description": "Carga Sustentada - Teste de estabilidade",
        "users": 100,
        "spawn_rate": 5,
        "duration": "30m",
        "k8s_config": {
            "voos_replicas": 3,
            "hoteis_replicas": 3,
            "gateway_replicas": 3,
            "hpa_enabled": True,
            "hpa_max_replicas": 10
        },
        "objetivo": "Verificar estabilidade com carga constante prolongada"
    },

    "cenario_7_gradual": {
        "description": "Crescimento Gradual - Avaliar autoscaling progressivo",
        "users": 250,
        "spawn_rate": 2,  # Crescimento lento
        "duration": "20m",
        "k8s_config": {
            "voos_replicas": 2,
            "hoteis_replicas": 2,
            "gateway_replicas": 2,
            "hpa_enabled": True,
            "hpa_max_replicas": 12
        },
        "objetivo": "Observar comportamento do HPA com crescimento gradual"
    },

    "cenario_8_resource_constrained": {
        "description": "Recursos Limitados - Teste com limits baixos",
        "users": 100,
        "spawn_rate": 10,
        "duration": "10m",
        "k8s_config": {
            "voos_replicas": 2,
            "hoteis_replicas": 2,
            "gateway_replicas": 2,
            "hpa_enabled": True,
            "hpa_max_replicas": 5,
            "cpu_limit": "100m",
            "memory_limit": "128Mi"
        },
        "objetivo": "Avaliar performance com recursos limitados"
    },

    "cenario_9_unbalanced": {
        "description": "Carga Desbalanceada - Mais réplicas em um serviço",
        "users": 150,
        "spawn_rate": 10,
        "duration": "10m",
        "k8s_config": {
            "voos_replicas": 5,  # Mais réplicas
            "hoteis_replicas": 2,
            "gateway_replicas": 4,
            "hpa_enabled": True
        },
        "objetivo": "Comparar desempenho com distribuição desbalanceada"
    },

    "cenario_10_optimal": {
        "description": "Configuração Otimizada - Baseado em resultados anteriores",
        "users": 200,
        "spawn_rate": 10,
        "duration": "15m",
        "k8s_config": {
            "voos_replicas": 4,
            "hoteis_replicas": 4,
            "gateway_replicas": 5,
            "hpa_enabled": True,
            "hpa_max_replicas": 15,
            "cpu_limit": "500m",
            "memory_limit": "512Mi"
        },
        "objetivo": "Validar configuração otimizada final"
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
