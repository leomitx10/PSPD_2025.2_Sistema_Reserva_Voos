#!/usr/bin/env python3
"""
Cenário 5: Teste de Estresse - Identificar breaking point
Objetivo: Encontrar o limite do sistema
"""

from run_single_scenario import run_scenario

SCENARIO = {
    "description": "Teste de Estresse - Identificar breaking point",
    "users": 150,
    "spawn_rate": 30,
    "duration": "5m",
    "hpa_enabled": True,
    "objetivo": "Encontrar o limite do sistema"
}

if __name__ == "__main__":
    exit(run_scenario("cenario_5_stress", SCENARIO))
