#!/usr/bin/env python3
"""
Cenário 3: Alta Carga - Teste de escalabilidade
Objetivo: Avaliar comportamento com alta demanda
"""

from run_single_scenario import run_scenario

SCENARIO = {
    "description": "Alta Carga - Teste de escalabilidade",
    "users": 50,
    "spawn_rate": 10,
    "duration": "5m",
    "hpa_enabled": True,
    "objetivo": "Avaliar comportamento com alta demanda"
}

if __name__ == "__main__":
    exit(run_scenario("cenario_3_high_load", SCENARIO))
