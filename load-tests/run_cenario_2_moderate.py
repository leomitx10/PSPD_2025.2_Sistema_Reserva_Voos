#!/usr/bin/env python3
"""
Cenário 2: Carga Moderada - HPA habilitado
Objetivo: Testar escalabilidade automática com carga moderada
"""

from run_single_scenario import run_scenario

SCENARIO = {
    "description": "Carga Moderada - HPA habilitado",
    "users": 30,
    "spawn_rate": 10,
    "duration": "5m",
    "hpa_enabled": True,
    "objetivo": "Testar escalabilidade automática com carga moderada"
}

if __name__ == "__main__":
    exit(run_scenario("cenario_2_moderate", SCENARIO))
